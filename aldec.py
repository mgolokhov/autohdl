import sys
import os
import re
import time
import shutil
import subprocess
import ConfigParser
import io

#import yaml
#from autohdl.lib.yaml import yaml
import autohdl.lib.yaml as yaml

import structure
import toolchain
import synthesis
import build
from hdlLogger import *


gWspScriptHeader = '''
  set wsp_name {wspName}
  set path_tmp {path_tmp}
  package require ::aldec::scripter 1.0 
  set ALDEC   [::aldec::scripter::GetVariable "ALDEC"]
  set DESIGNS [::aldec::scripter::GetVariable "DESIGNS"]
  set WSP     [::aldec::scripter::GetVariable "WSP"]
  set DSN     [::aldec::scripter::GetVariable "DSN"]
  if [file exists "$path_tmp/aldec"] {LCB}
    file delete "$path_tmp/aldec"
  {RCB}
  echofile "$path_tmp/aldec" "DESIGNS=$DESIGNS\\n"
  # create workspace      
  file mkdir "$DESIGNS/$wsp_name"
  workspace create "$DESIGNS/$wsp_name/$wsp_name"
  workspace open "$DESIGNS/$wsp_name/$wsp_name"
  '''

# all operations from <dsn_name>/script/
gPathTmp = '../aldec'

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
  
  dict['other'] = other
  dict['main'] = main
  dict['dep'] = dep
  dict['TestBench'] = TestBench
  dict['netlist'] = structure.search(iPath = '../aldec/src',
                                     iOnly = ['\.sedif', '\.edn', '\.edf', '\.edif', '\.ngc' ])  
  
  
  return dict

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


def gen_aws():
  content = '[Designs]\ndsn=./dsn.adf'
  f = open('../aldec/wsp.aws', 'w')
  f.write(content)
  f.close()


def gen_adf_helper(iKey, iStructure):
  rootPath = iStructure['rootPath']+'/'
  list = []
  for i in iStructure[iKey]:
    virtFolder = os.path.dirname(i).replace('\\', '/').split(rootPath)[1]
    virtFolder = virtFolder.replace('/', '\\')
    list.append(virtFolder + '/' + i + '=-1')
  return list
  
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
  
  f = open('../aldec/dsn.adf', 'w')
  config.write(f)
  f.close()


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
  

def cleanAldec():
  cl = structure.search(iPath = '../aldec', iIgnore = ['/implement/', '/synthesis/', '/src/'])
  for i in cl:
    if os.path.isdir(i):
      shutil.rmtree(i)
    else:
      os.remove(i)

def copyNetlists():
  netLists = structure.search(iPath = '..',
                              iOnly = ['\.sedif', '\.edn', '\.edf', '\.edif', '\.ngc' ],
                              iIgnore = ['\.git', '\.svn', '/aldec/'])
  for i in netLists:
    shutil.copyfile(i, '../aldec/src/'+os.path.split(i)[1])

def export():
  cleanAldec()
  for i in structure.gPredefined:
    folder = '../aldec/src/'+i
    if not os.path.exists(folder):
      os.makedirs(folder)
  copyNetlists()
  prjStructure = getStructure()
  gen_aws()
  gen_adf(iStructure = prjStructure)
  filesToCompile = prjStructure['main'] + prjStructure['dep'] + prjStructure['TestBench']
  gen_compile_cfg(iFiles = filesToCompile)
  build.dump(iStructure = prjStructure)
  
    
  subprocess.Popen('python ' + os.path.dirname(__file__) + '/aldec_run.py')  
    
######################################################################
######################################################################
######################################################################
def getPathTmp(iDsn = ''):
  '''
  Defines and creates temporary folder.
  '''
  if iDsn:
    global gPathTmp
    gPathTmp = iDsn.pathRoot+'/aldec'
  if not os.path.exists(gPathTmp):
    os.makedirs(gPathTmp)
  return gPathTmp


def getAldecVar(iPathTmp, iVar):
  '''
  Extracts specific variable of Aldec software
  '''
  log.debug('def getAldecVar: iPathTmp=' + iPathTmp + 'iVar=' + iVar)
  pathFile = iPathTmp+'/aldec'
  if not os.path.exists(pathFile):
    log.warning('Cant find file: ' + pathFile)
    return ''
  f = open(pathFile, 'r')
  fileContent = f.read()
  f.close()
  match = re.search(iVar + '=(.*?)\n', fileContent)
  var = ''
  if match:
    print match.group()
    var = match.group(1)
  else:
    log.warning('Cant find variable '+iVar+' in file '+pathFile)
  return var



def genScriptWsp(iWspName, iPathDir):
  '''
  Generates tcl script for Aldec to create a workspace;
  Input: iWspName, iPathDir - directory in which a script will be generated;
  '''
  log.debug('def genScriptWsp IN iWsnName='+iWspName+'; iPath='+iPathDir)

  scriptContent = (gWspScriptHeader + '''
  closedocument -all
  runscript "{path_tmp}/mk_dsn.do"
  file mkdir "{path_tmp}/done"\n''')\
  .format(wspName = iWspName,
          path_tmp = iPathDir,
          LCB = '{', RCB = '}')
  
  f = open(iPathDir+'/mk_wsp.tcl', 'w')
  f.write(scriptContent)
  f.close()


def genScriptDsn(iDsn, iPathDir, iPrjName, iTopModule = ''):
  '''
  Generates .do script for Aldec to create a design.
  Use it as auxiliary script to .tcl one.
  Input: iDsnName, iPathDir - directory in which a script will be generated;
  '''
  log.debug('def genScriptDsn IN iDsn='+str(iDsn)+'\n iPathDir='+iPathDir)
  f = open(iPathDir + '/mk_dsn.do', 'w')
  f.write((
  'design create -a -flow "{0}" "$WSP"\n'+ 
  'design activate "{0}"\n').format(iPrjName))
  
  #include files in design
  for fileMain in iDsn.filesMain:
    dir = os.path.dirname(fileMain).replace(iDsn.pathRoot+'/','')
    f.write('addfile -dir "' + dir + '" "' + fileMain + '"\n')
  
  #include dependency files
  for fileDep in iDsn.filesDep:
    f.write('addfile -dir dep "' + fileDep + '"\n')
  
  files = list(iDsn.filesMain) + list(iDsn.filesDep)
  filesString = '\ncomp -include '.join(files)    
  comp = '''    
  SetActiveLib -work
  #Compiling UUT module design files
  comp -include {filesToCompile}
  '''.format(filesToCompile=filesString) 
  f.write(comp)   

  if iTopModule:
    f.write('''
    asim +access +r {top}
    wave
    '''.format(top = iTopModule))
  
  f.close()


#precondition:
#  input: dsnFiles, topModule
def gen_script_tb(iTopModule, iDsn):
  '''
  Generates .tcl script for Aldec to create and run TestBench design.  
  '''
  log.debug('def gen_script_tb IN iTopModule='+iTopModule+' iDsn=\n'+str(iDsn))
  pathTmp = getPathTmp(iDsn)
  f = open(pathTmp +'/'+ iTopModule + '.tcl', 'w')
  scriptContent = (gWspScriptHeader + '''
  opendocument -do "{path_tmp}/{wspName}.do"
  runscript "{path_tmp}/{wspName}.do"\n''')\
  .format(wspName = iTopModule,
          path_tmp = pathTmp,
           LCB = '{', RCB = '}')
  
  f.write(scriptContent)
  f.close()

  f = open(pathTmp +'/'+ iTopModule + '.do', 'w')
  f.write(
  'design create -a -flow "' + iTopModule + '" "$WSP"\n' + 
  'design activate "' + iTopModule + '"\n')
  filesMain = structure.search(iPath = '..', iIgnore = ['\.svn/'], iOnly = ['src/', 'TestBench/'])
  log.debug('filesMain= '+str(filesMain))
  filesDep = list(structure.getDepSrc(iSrc = filesMain))
  log.debug('filesDep= '+str(filesDep))
  for dsnFile in filesMain + filesDep:
    pathAsList = dsnFile.split('/')
    if dsnFile in filesDep:
      add_dir = 'dep'
    else:
      add_dir = '/'.join(pathAsList[pathAsList.index(iDsn.name)+1:-1])
    if os.path.isfile(dsnFile):
      f.write('addfile -dir "' + add_dir + '" "' + dsnFile + '"\n')

  files = filesMain + filesDep
  filesString = '\ncomp -include '.join(files)

  runScript = '''    
  SetActiveLib -work
  #Compiling UUT module design files
  comp -include {filesToCompile}
  
  asim +access +r {module_tb}
  
  wave
  
  run 1ns    
  '''.format(module_tb=iTopModule,
             filesToCompile=filesString) 
  
  f.write(runScript)   
    
  f.close()


def gen(iTopModule, iPrjName, iDsn):
  '''
  Generates all scripts to create a design.
  '''
  log.debug('def gen IN ')
  path = getPathTmp()
  genScriptWsp(iWspName = iPrjName, iPathDir = path)
  genScriptDsn(iTopModule = iTopModule, iDsn = iDsn, iPathDir = path, iPrjName = iPrjName)

    
def gen_run(iTopModule, iPrjName, iDsn):
  '''
  Generates scripts for design creation and runs them in Aldec.
  '''
  log.debug('def gen_run IN iTopModule='+iTopModule+' iPrjName='+iPrjName)
  gen(iTopModule=iTopModule, iPrjName = iPrjName, iDsn = iDsn)

  if os.path.exists(getPathTmp() + '/done'):
    shutil.rmtree(getPathTmp() + '/done')
  avhdl_gui = toolchain.getPath('avhdl_gui')
  subprocess.Popen([avhdl_gui, getPathTmp()+'/mk_wsp.tcl'])
  
  while True:
    time.sleep(1)
    if os.path.exists(getPathTmp() + '/done'):
      break
#    
#  if os.path.exists(getPathTmp(iPrj)):
#    shutil.rmtree(getPathTmp(iPrj))


def clean(iPath, iPrjName):
  '''
  Cleans previously created design with the same name.
  '''
  log.debug('def clean IN iPath='+iPath+' iName='+iPrjName)
  aldecDesigns = getAldecVar(iPathTmp = iPath, iVar = 'DESIGNS')
  wsp = aldecDesigns+'/'+iPrjName
  if aldecDesigns and os.path.exists(wsp):
    shutil.rmtree(wsp)
    print 'wsp to del=', wsp

      

def setPrjName(iDsnName, iTopModule = '', iPrjName = ''):
  if iPrjName:
    name = iPrjName
  elif iTopModule:
    name = iTopModule
  else:
    name = iDsnName
  return name


# BUGAGA: first of all tb
def tb(iTopModule, iPrjName = '', iClean = False):
  '''
  Runs TestBench design.
  '''
  log.debug('def tb IN iTopModule='+iTopModule+' iPrjName='+iPrjName+' iClean='+str(iClean))
  dsn = structure.Design(iPath = '..', iGen = False, iInit = False)
  #include files in design
  only = []
  dir = ['src/', 'TestBench/']
  ext = build.getSrcExtensions(iTag = 'synthesis_ext')
  for i in ext:
    for j in dir: 
      only.append(j + '.*?\.' + i + '$')
  ignore = ['\.svn/', 'implement/', 'synthesis/']
  dsn.filesMain = structure.search(iPath = '..', iIgnore = ignore, iOnly = only)
  ignore.append('TestBench/')
  dsn.filesDep = structure.getDepSrc(iSrc = dsn.filesMain, iIgnore = ignore, iOnly = only)
  global gPathTmp
  gPathTmp = dsn.pathRoot+'/aldec'

  prjName = setPrjName(iDsnName = dsn.name, iTopModule = iTopModule, iPrjName = iPrjName)

  if iClean:
    clean(iPath = gPathTmp, iPrjName = prjName)

  gen_run(iTopModule=iTopModule, iPrjName = prjName, iDsn = dsn)
  log.debug('def tb OUT')
  

  
if __name__ == '__main__':
#  res = yaml.load(t)
#  print res.get('synthesis')
#  print yaml.dump(res, default_flow_style=False)
#  print res.get('key3')
  pass

  
  