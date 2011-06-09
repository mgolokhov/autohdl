import sys
import os
import re
import time
import shutil
import subprocess
import ConfigParser
import io
import sqlite3

import autohdl.lib.yaml as yaml

from hdlLogger import log_call
import logging
import structure
import toolchain
import synthesis
import build
import hdlGlobals


gPrj = ''


@log_call
def getStructure():
  '''
  Precondition: cwd= <dsn_name>/script
  Output: dictionary { keys=main, dep, tb, other values=list of path files}
  '''
  preparation()
  dict = {}
  dict['rootPath'] = os.path.abspath('..').replace('\\', '/')
  dict['dsnName'] = os.path.split(dict['rootPath'])[1]
  
  allSrc = []
  ignore = hdlGlobals.ignore
  for i in ['../src', '../TestBench', '../script', '../resource']:
    allSrc += structure.search(iPath = i, iIgnore = ignore)
  dict['allSrc'] = allSrc

  mainSrc = structure.search(iPath = '../src',
                                     iOnly = ['\.v', '\.vm', '\.vhdl', '\.vhd'],
                                     iIgnore = ignore)
  dict['mainSrc'] = mainSrc
  dict['depSrc'] = structure.getDepSrc(iSrc = mainSrc, iIgnore = ignore)
  
  dict['TestBenchSrc'] = structure.search(iPath='../TestBench', iIgnore = ignore)
  

  dict['netlistSrc'] = structure.search(iPath = '../aldec/src',
                                        iOnly = ['\.sedif', '\.edn', '\.edf', '\.edif', '\.ngc' ])     
  global gPrj
  gPrj = dict
   
  return dict


@log_call
def gen_aws(iStructure):
  content = '[Designs]\n{dsn}=./{dsn}.adf'.format(dsn=iStructure['dsnName'])
  f = open('../aldec/wsp.aws', 'w')
  f.write(content)
  f.close()


@log_call
def preprFiles():
  dep  = ['dep/' + i + '=-1' for i in gPrj['depSrc']]
  netlist = ['/'+ i + '=-1' for i in gPrj['netlistSrc']]
  
  allOtherSrc = list(set(gPrj['allSrc']) - set(gPrj['depSrc']))
  rootPath = gPrj['rootPath']+'/'
  l = []
  for i in allOtherSrc:
    virtFolder = os.path.dirname(i).replace('\\', '/').split(rootPath)[1]
    virtFolder = virtFolder.replace('/', '\\')
    l.append(virtFolder + '/' + i + '=-1')
  allOtherSrc = l
  files = '\n'.join(dep + netlist + allOtherSrc)
  return files


@log_call
def preprFilesData():
  srcTb = ['.\\' + os.path.relpath(i) + '=Verilog Test Bench'
            for i in gPrj['TestBenchSrc']
            if os.path.splitext(i)[1] in ['.v']]
  filesData = '\n'.join(srcTb)
  return filesData


@log_call
def preprLocalVerilogDirs(iArg):
  res = iArg.split(';')
  counter = 'Count={0}'.format(len(res))
  inclDir = ['IncludeDir{0}={1}'.format(i, path) for i, path in enumatate(res)]
  return counter + '\n'.join(inclDir)


@log_call
def getFromDB(iKey, _cache = []):
  if not _cache:
    aconnect = sqlite3.connect(os.path.join(os.path.dirname(__file__),'data', 'autohdl.db'))
    acursor = aconnect.cursor()
    _cache.append(acursor)
  else:
    acursor = _cache[0]
  ex = 'SELECT * FROM aldec WHERE adf = "{0}"'.format(iKey)
  acursor.execute(ex)
  adf, ayaml, bydefault, preprocess = acursor.fetchone()
  if ayaml:
    yamlVal = build.getParam(ayaml.upper())
    if yamlVal:
      if preprocess:
        res = eval(preprocess)(yamlVal)
      else:
        res = yamlVal
    else:
      res = bydefault
  elif bydefault:
    res = bydefault
  else:
    res = eval(preprocess)()

  return res




@log_call
def gen_adf(iPrj):
  templateAdf = os.path.join(os.path.dirname(__file__), 'data', 'template_aldec_adf')
  contentAdf = open(templateAdf, 'r').read()
  config = ConfigParser.RawConfigParser(allow_no_value=True)
  config.optionxform = str
  config.readfp(io.BytesIO(contentAdf))
  
  for section in config.sections():
    for option in config.options(section):
      
      if option.startswith('{') and option.endswith('}'):
        config.remove_option(section, option)
        config.set(section, getFromDB(iKey = option[1:-1]))
        continue
      
      val = config.get(section, option)
      if val and val.startswith('{') and val.endswith('}'):
        config.set(section, option, getFromDB(iKey = val[1:-1]))  
  
  f = open('../aldec/{dsn}.adf'.format(dsn=iPrj['dsnName']), 'w')
  config.write(f)
  f.close()



@log_call
def gen_compile_cfg(iFiles):
  src = [] 
  start = os.path.dirname('../aldec/compile.cfg')
  for i in iFiles:
    path = os.path.abspath(i)
    try:
      res = '[file:.\\' + os.path.relpath(path = path, start = start) + ']\nEnabled=1'
    except ValueError:
      res = '[file:' + i + ']\nEnabled=1'
    src.append(res)
      
  content = '\n'.join(src)
  f = open('../aldec/compile.cfg', 'w')
  f.write(content)
  f.close()
  

@log_call
def cleanAldec():
  cl = structure.search(iPath = '../aldec', iIgnore = ['/implement/', '/synthesis/', '/src/'])
  for i in cl:
    if os.path.isdir(i):
      shutil.rmtree(i)
    else:
      os.remove(i)


@log_call
def copyNetlists():
  netLists = structure.search(iPath = '../src',
                              iOnly = ['\.sedif', '\.edn', '\.edf', '\.edif', '\.ngc' ],
                              iIgnore = ['\.git', '\.svn', '/aldec/'])
  for i in netLists:
    shutil.copyfile(i, '../aldec/src/'+os.path.split(i)[1])

@log_call
def genPredefined():
  predef = structure.gPredefined + ['dep']
  for i in predef:
    folder = '../aldec/src/'+i
    if not os.path.exists(folder):
      os.makedirs(folder)

@log_call
def preparation():  
  cleanAldec()
  genPredefined()
  copyNetlists()

@log_call
def export():
  preparation()
  getStructure() # same as gPrj
  prj = gPrj
  gen_aws(iStructure = prj)
  gen_adf(iPrj = prj)
  filesToCompile = prj['mainSrc'] + prj['depSrc'] + prj['TestBenchSrc']
  gen_compile_cfg(iFiles = filesToCompile)
  build.dump(iStructure = prj)

  subprocess.Popen('pythonw ' + os.path.dirname(__file__) + '/aldec_run.py '+ os.getcwd())  
