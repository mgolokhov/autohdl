import sys
import os
import re
import time
import shutil
import subprocess

import structure
import toolchain
import synthesis
from hdlLogger import *


wsp_script_header = '''
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

def getPathTmp(iArg):
  '''
  Defines and creates temporary folder.
  '''
  pathTmp = iArg.pathRoot + '/.tmp'
  if not os.path.exists(pathTmp):
    os.makedirs(pathTmp)
  return pathTmp


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


#precondition:
#  input: wspName, path 
def genScriptWsp(iPrj):
  '''
  Generates tcl script for Aldec to create a workspace
  '''
  log.debug('def genScriptWsp: ' + str(iPrj))
  wspName = iPrj.wspName
  pathTmp = getPathTmp(iPrj)

  scriptContent = (wsp_script_header + '''
  runscript "{path_tmp}/mk_dsn.do"
  closedocument -all
  file mkdir "{path_tmp}/done"\n''')\
  .format(wspName = wspName,
          path_tmp = pathTmp,
          LCB = '{', RCB = '}')
  
  f = open(pathTmp+'/mk_wsp.tcl', 'w')
  f.write(scriptContent)
  f.close()
  return scriptContent


#precondition:
#  input: dsnName, dsnFiles, pathTmp
def genScriptDsn(iDsn, iPathTmp):
  '''
  Generates .do script for Aldec to create a design.
  Use it as auxiliary script to .tcl one.
  '''
  log.warning('def genScriptDsn: iDsn='+str(iDsn)+' iPathTmp='+iPathTmp)
  dsnName = iDsn.dsnName
  f = open(iPathTmp + '/mk_dsn.do', 'a')
  f.write(
  'design create -a -flow "' + dsnName + '" "$WSP"\n' + 
  'design activate "' + dsnName + '"\n')
  
  ignore = ['.tmp', 'implement', 'synthesis']
  
  #include files in design
  filesMain = iDsn.getFileMain(iIgnore = ignore)
  for fileMain in filesMain:
    pathAsList = fileMain.split('/')
    addDir = '/'.join(pathAsList[pathAsList.index(dsnName)+1:-1])
    f.write('addfile -dir "' + addDir + '" "' + fileMain + '"\n')
  
  #include dependency files
  filesDep = iDsn.getDep()
  for fileDep in filesDep:
    f.write('addfile -dir dep "' + fileDep + '"\n')
  
  #include empty folders  
  dirsMain = iDsn.getDirMain(iIgnore = ignore)
  for dirMain in dirsMain:
    pathAsList = dirMain.split('/')
    addDir = '/'.join(pathAsList[pathAsList.index(dsnName)+1:]) 
    f.write('addfolder "' + addDir + '"\n')
    
  f.close()


#precondition:
#  input: dsnFiles, topModule
def gen_script_tb(iTopModule, iDsn):
  '''
  Generates .tcl script for Aldec to create and run TestBench design.  
  '''
  log.debug('def gen_script_tb: iTopModule='+iTopModule+' iDsn=\n'+str(iDsn))
  pathTmp = getPathTmp(iDsn)
  f = open(pathTmp +'/'+ iTopModule + '.tcl', 'w')
  scriptContent = (wsp_script_header + '''
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
  filesMain = iDsn.getFileMain(iOnly = ['src', 'TestBench'])
#  filesDep = list(iDsn.getDeps())
  filesDep = list(iDsn.getFileDep())
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




def gen(iPrj):
  '''
  Generates all scripts to create a design.
  '''
  log.debug('def gen: iPrj='+str(iPrj))
  genScriptWsp(iPrj)
  path = getPathTmp(iPrj)
  
  pathDel = path + '/mk_dsn.do'
  if os.path.exists(pathDel):
    os.remove(pathDel)
  
  #BUGAGA: wsp VS dsn generation (tmp files)
  for dsn in iPrj.dsnList:
    genScriptDsn(dsn, getPathTmp(iPrj))

    
def gen_run(iPrj):
  '''
  Generates scripts for design creation and runs them in Aldec.
  '''
  log.debug('def gen_run: iPrj='+iPrj)
  gen(iPrj)

  avhdl_gui = toolchain.getPath('avhdl_gui')
  subprocess.Popen([avhdl_gui, getPathTmp(iPrj)+'/mk_wsp.tcl'])
  
#  while True:
#    time.sleep(1)
#    print getPathTmp(iPrj) + '/done'
#    if os.path.exists(getPathTmp(iPrj) + '/done'):
#      break
#    
#  if os.path.exists(getPathTmp(iPrj)):
#    shutil.rmtree(getPathTmp(iPrj))


def clean(iPath, iName):
  '''
  Cleans previously created design with the same name.
  '''
  log.debug('def clean: iPath='+iPath+' iName='+iName)
  aldecDesigns = getAldecVar(iPathTmp = iPath, iVar = 'DESIGNS')
  wsp = aldecDesigns+'/'+iName
  if aldecDesigns and os.path.exists(wsp):
    shutil.rmtree(wsp)

      
def export(iClean = False):
  '''
  Exports all design in Aldec.
  '''
  log.debug('def export: iClean='+str(iClean))
  dsn = structure.Design('..')
  path = getPathTmp(dsn)
  if iClean:
    clean(path, dsn.name)
  gen_run(dsn)
  log.info('Export done')
  return dsn

# BUGAGA: twice calling getDeps
def tb(iTopModule, iClean = False):
  '''
  Runs TestBench design.
  '''
  log.debug('def tb: iTopModule<='+iTopModule+' iClean='+str(iClean))
  dsn = structure.Design(iPath = '..')
  log.debug('dsn=\n'+str(dsn))
  path = getPathTmp(dsn)
  
  if iClean:
    clean(path, iTopModule)

  gen_script_tb(iTopModule = iTopModule, iDsn = dsn)
    
  avhdl_gui = toolchain.getPath('avhdl_gui')
  subprocess.Popen([avhdl_gui, getPathTmp(dsn) +'/'+ iTopModule +'.tcl'])
  log.debug('def tb=>')
  
  