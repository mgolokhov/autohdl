import sys
import os
import re
import time
import shutil
import subprocess
import ConfigParser
import io

import autohdl.lib.yaml as yaml
from hdlLogger import *
import structure
import toolchain
import synthesis
import build


@log_call
def getStructure():
  '''
  Precondition: cwd= <dsn_name>/script
  Output: dictionary { keys=main, dep, tb, other values=list of path files}
  '''
  dict = {}
  only = build.getParam('only_regexp')
  ignore = build.getParam('ignore_regexp')
  dict['rootPath'] = os.path.abspath('..').replace('\\', '/')
  
  other = []
  for i in ['../src', '../TestBench', '../script', '../resource']:
    other += structure.search(iPath = i, iIgnore = ignore)

  main = structure.search(iPath = '../src',
                          iOnly = ['\.v', '\.vm', '\.vhdl', '\.vhd'],
                          iIgnore = ignore)
  dep = list(structure.getDepSrc(iSrc=main, iIgnore = ignore))
  TestBench = structure.search(iPath='../TestBench', iIgnore = ignore, iOnly = only)
  
  other = list(set(other) - set(main) - set(dep) - set(TestBench))
  
  dict['dsnName'] = os.path.split(dict['rootPath'])[1]
  dict['other'] = other
  dict['main'] = main
  dict['dep'] = dep
  dict['TestBench'] = TestBench
  dict['netlist'] = structure.search(iPath = '../aldec/src',
                                     iOnly = ['\.sedif', '\.edn', '\.edf', '\.edif', '\.ngc' ],
                                     iIgnore = ['aldec/src/src/'])  
  
  
  return dict


@log_call
def synch_adf(iBuildContent):
  pathDefaultAdf = os.path.join(os.path.dirname(__file__), 'data', 'aldec_adf')
  contentAdf = open(pathDefaultAdf, 'r').read()
  config = ConfigParser.RawConfigParser(allow_no_value=True)
  config.optionxform = str
  config.readfp(io.BytesIO(contentAdf))
  for key in iBuildContent:
    for section in config.sections():
      try:
        config.get(section, key)
        config.set(section, key, iBuildContent[key])
      except ConfigParser.NoOptionError:
        continue 
  return config


@log_call
def gen_aws(iStructure):
  content = '[Designs]\n{dsn}=./{dsn}.adf'.format(dsn=iStructure['dsnName'])
  f = open('../aldec/wsp.aws', 'w')
  f.write(content)
  f.close()


@log_call
def gen_adf_helper(iKey, iStructure):
  rootPath = iStructure['rootPath']+'/'
  list = []
  for i in iStructure[iKey]:
    virtFolder = os.path.dirname(i).replace('\\', '/').split(rootPath)[1]
    virtFolder = virtFolder.replace('/', '\\')
    list.append(virtFolder + '/' + i + '=-1')
  return list


  
@log_call
def gen_adf(iStructure):
  main = gen_adf_helper(iKey = 'main', iStructure = iStructure)
  dep  = ['dep/' + i + '=-1' for i in iStructure['dep']]
  tb = gen_adf_helper(iKey = 'TestBench', iStructure = iStructure)
  other = gen_adf_helper(iKey = 'other', iStructure = iStructure)
  netlist = ['/'+ i + '=-1' for i in iStructure['netlist']]
  src_all = '\n'.join(main+dep+tb+other+netlist)
  
  src_tb = ['.\\' + os.path.relpath(i) + '=Verilog Test Bench'
            for i in iStructure['TestBench']
            if os.path.splitext(i)[1] in ['.v']]
  src_tb = '\n'.join(src_tb)

  config = synch_adf(iBuildContent = build.load())
  config.set('Files', src_all)
  config.set('Files.Data', src_tb)
  
  f = open('../aldec/{dsn}.adf'.format(dsn=iStructure['dsnName']), 'w')
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
def export():
  cleanAldec()
  for i in structure.gPredefined:
    folder = '../aldec/src/'+i
    if not os.path.exists(folder):
      os.makedirs(folder)
  copyNetlists()
  prjStructure = getStructure()
  gen_aws(iStructure = prjStructure)
  gen_adf(iStructure = prjStructure)
  filesToCompile = prjStructure['main'] + prjStructure['dep'] + prjStructure['TestBench']
  gen_compile_cfg(iFiles = filesToCompile)
  build.dump(iStructure = prjStructure)

  subprocess.Popen('pythonw ' + os.path.dirname(__file__) + '/aldec_run.py')  
