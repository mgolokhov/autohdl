import os
import shutil
import subprocess


from autohdl.hdlLogger import log_call
from autohdl import structure
from autohdl import build
from autohdl import hdlGlobals
from autohdl import template_avhdl_adf
from autohdl import toolchain
import sys


@log_call
def extend(config):
  """
  Precondition: cwd= <dsn_name>/script
  Output: dictionary { keys=main, dep, tb, other values=list of path files}
  """
  config['rootPath'] = os.path.abspath('..').replace('\\', '/')
  config['dsnName'] = os.path.split(config['rootPath'])[1]
  
  allSrc = []
  ignore = hdlGlobals.ignore
  for i in ['../src', '../TestBench', '../script', '../resource']:
    allSrc += structure.search(iPath = i, iIgnore = ignore)
  config['allSrc'] = allSrc


  mainSrcUncopied = structure.search(iPath = '../aldec/src',
                                     iOnly = hdlGlobals.verilogFileExtRe+hdlGlobals.vhdlFileExtRe,
                                     iIgnore = hdlGlobals.ignoreRepoFiles)
  config['srcUncopied'] = mainSrcUncopied

  config['TestBenchSrc'] = structure.search(iPath='../TestBench', iIgnore = hdlGlobals.ignoreRepoFiles)
  

  config['netlistSrc'] = structure.search(iPath = '../aldec/src',
                                        iOnly = ['\.sedif', '\.edn', '\.edf', '\.edif', '\.ngc' ])

  config['filesToCompile'] = config['mainSrc'] + config['depSrc'] + config['TestBenchSrc'] + mainSrcUncopied

  #TODO: bugaga
  path = os.path.abspath(os.getcwd())
  pathAsList = path.replace('\\', '/').split('/')
  if pathAsList[-3] == 'cores':
    repoPath = '/'.join(pathAsList[:-3])
  else:
    repoPath = '/'.join(pathAsList[:-2])
  config['repoPath'] = repoPath
#  print repoPath
  repoSrc = []
  for root, dirs, files in os.walk(repoPath):
    if config['dsnName'] in dirs:
      dirs.remove(config['dsnName'])
    for i in ['aldec', 'synthesis', 'implement', '.svn', '.git', 'TestBench', 'script', 'resource']:
      if i in dirs:
        dirs.remove(i)
    for f in files:
      if 'src' in root+'/'+f:
        repoSrc.append(os.path.abspath(root+'/'+f).replace('\\', '/'))
  config['repoSrc'] = repoSrc
  config['build'] = build.load()


@log_call
def gen_aws(iPrj):
  content = '[Designs]\n{dsn}=./{dsn}.adf'.format(dsn=iPrj['dsnName'])
  with open('../aldec/wsp.aws', 'w') as f:
    f.write(content)


@log_call
def gen_adf(iPrj):
  adf = template_avhdl_adf.generate(iPrj = iPrj)
  with open('../aldec/{dsn}.adf'.format(dsn=iPrj['dsnName']), 'w') as f:
    f.write(adf)


@log_call
def gen_compile_cfg(iFiles, iRepoSrc):
  filesSet = set(iFiles)
  iFiles = list(filesSet)
  iRepoSrc = list(set(iRepoSrc)-filesSet)
  src = [] 
  start = os.path.dirname('../aldec/compile.cfg')
  for i in iFiles:
    if os.path.splitext(i)[1] not in hdlGlobals.srcFileTypes:
      continue
    path = os.path.abspath(i)
    try:
      res = '[file:.\\{0}]\nEnabled=1'.format(os.path.relpath(path = path, start = start))
    except ValueError:
      res = '[file:{0}]\nEnabled=1'.format(i)
    src.append(res)

  for i in iRepoSrc:
    if i not in hdlGlobals.srcFileTypes:
      continue
    path = os.path.abspath(i)
    try:
      res = '[file:.\\{0}]\nEnabled=0'.format(os.path.relpath(path = path, start = start))
    except ValueError:
      res = '[file:{0}]\nEnabled=0'.format(i)
    src.append(res)

  content = '\n'.join(src)
  f = open('../aldec/compile.cfg', 'w')
  f.write(content)
  f.close()
  

@log_call
def cleanAldec():
  if not {'aldec', 'script', 'src'}.issubset(os.listdir(os.getcwd()+'/..')):
    return
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
def export(config):
  preparation()
  extend(config)
  gen_aws(config)
  gen_adf(config)
  gen_compile_cfg(iFiles = config['allSrc']+config['depSrc'], iRepoSrc=config['repoSrc']) # prj['filesToCompile'])
  aldec = toolchain.Tool().get('avhdl_gui')
  subprocess.Popen('python{3} {0}/aldec_run.py {1} "{2}"'.format(
                                                            os.path.dirname(__file__),
                                                            os.getcwd(),
                                                            aldec,
                                                            '' if config.get('debug') else 'w'
                                                            ))
