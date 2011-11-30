import os
import shutil
import subprocess


from autohdl.hdlLogger import log_call
from autohdl import structure
from autohdl import build
from autohdl import hdlGlobals
from autohdl import template_avhdl_adf
from autohdl import toolchain



@log_call
def initPrj():
  """
  Precondition: cwd= <dsn_name>/script
  Output: dictionary { keys=main, dep, tb, other values=list of path files}
  """
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

  mainSrcUncopied = structure.search(iPath = '../aldec/src',
                           iOnly = ['\.v', '\.vm', '\.vhdl', '\.vhd'],
                           iIgnore = ignore)
  dict['srcUncopied'] = mainSrcUncopied
  dict['mainSrc'] = mainSrc
  dict['depSrc'] = structure.getDepSrc(iSrc = mainSrc, iIgnore = ignore)

  dict['TestBenchSrc'] = structure.search(iPath='../TestBench', iIgnore = ignore)
  

  dict['netlistSrc'] = structure.search(iPath = '../aldec/src',
                                        iOnly = ['\.sedif', '\.edn', '\.edf', '\.edif', '\.ngc' ])

  dict['filesToCompile'] = dict['mainSrc'] + dict['depSrc'] + dict['TestBenchSrc'] + mainSrcUncopied

  #TODO: bugaga
  path = os.path.abspath(os.getcwd())
  pathAsList = path.replace('\\', '/').split('/')
  if pathAsList[-3] == 'cores':
    repoPath = '/'.join(pathAsList[:-3])
  else:
    repoPath = '/'.join(pathAsList[:-2])
  dict['repoPath'] = repoPath
#  print repoPath
  repoSrc = []
  for root, dirs, files in os.walk(repoPath):
    if dict['dsnName'] in dirs:
      dirs.remove(dict['dsnName'])
    for i in ['aldec', 'synthesis', 'implement', '.svn', '.git', 'TestBench', 'script', 'resource']:
      if i in dirs:
        dirs.remove(i)
    for f in files:
      if 'src' in root+'/'+f:
        repoSrc.append(os.path.abspath(root+'/'+f).replace('\\', '/'))
  dict['repoSrc'] = repoSrc
  dict['build'] = build.load()

  return dict


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
    path = os.path.abspath(i)
    try:
      res = '[file:.\\{0}]\nEnabled=1'.format(os.path.relpath(path = path, start = start))
    except ValueError:
      res = '[file:{0}]\nEnabled=1'.format(i)
    src.append(res)

  for i in iRepoSrc:
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


#TODO: add arguments top, ucf, test
@log_call
def export():
  preparation()
  prj = initPrj()
  gen_aws(iPrj = prj)
  gen_adf(iPrj = prj)
  gen_compile_cfg(iFiles = prj['allSrc']+prj['depSrc'], iRepoSrc=prj['repoSrc']) # prj['filesToCompile'])
  if build.getParam(iKey = 'test'):
    return
  aldec = toolchain.getPath(iTag = 'avhdl_gui')
  subprocess.Popen('pythonw {0}/aldec_run.py {1} "{2}"'.format(
                                                            os.path.dirname(__file__),
                                                            os.getcwd(),
                                                            aldec
                                                            ))
