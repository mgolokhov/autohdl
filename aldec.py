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




gContentAdf = r'''
[Project]
Current Flow=Multivendor
VCS=0
version=3
Current Config=compile

[Settings]
AccessRead=0
AccessReadWrite=0
AccessACCB=0
AccessACCR=0
AccessReadWriteSLP=0
AccessReadTopLevel=1
DisableC=1
ENABLE_ADV_DATAFLOW=0
FLOW_TYPE=HDL
LANGUAGE=VERILOG
REFRESH_FLOW=1
SYNTH_TOOL=MV_SYNPLIFY_PREMIER_C2009_06
RUN_MODE_SYNTH=1
IMPL_TOOL=MV_ISE111
CSYNTH_TOOL=<none>
PHYSSYNTH_TOOL=<none>
FLOWTOOLS=IMPL_WITH_SYNTH
ON_SERVERFARM_SYNTH=0
ON_SERVERFARM_IMPL=0
ON_SERVERFARM_SIM=0
DVM_DISPLAY=NO
VerilogDirsChanged=1
FAMILY=Xilinx11x SPARTAN3E
SYNTH_STATUS=none
IMPL_STATUS=none
RUN_MODE_IMPL=0


[IMPLEMENTATION]
FLOW_STEPS_RESET=0
UCF=
DEVICE_TECHNOLOGY_MIGRATION_LIST=
FAMILY=Xilinx11x SPARTAN3E
DEVICE=3s250etq144
SPEED=-5
IS_BAT_MODE=0
BAT_FILE=
NETLIST=
DEF_UCF=2
OLD_FAMILY=Xilinx11x SPARTAN3E
wasChanged_Change_Device_Speed=0
wasChanged_Change_Device_Speed_To=0
wasChanged_Change_Device_Speed_To2=0
Place_And_Route_Mode_old_value=Normal
JOB_DESCRIPTION=ImplementationTask
SERVERFARM_INCLUDE_INPUT_FILES=*.*
SERVERFARM_EXCLUDE_INPUT_FILES=log\*.*
JOB_SFM_RESOURCE=
SYNTH_TOOL_RESET=0

[SYNTHESIS]
DEVICE_SET_FLAG=1
OBSOLETE_ALIASES=1
VIEW_MODE=RTL
TOPLEVEL=
FAMILY=Xilinx11x SPARTAN3E
OLD_FAMILY=Xilinx11x SPARTAN3E
DEVICE=3s250etq144
SPEED=-5
ADDITIONAL_OPTIONS_ON_STARTUP=
FORCE_GSR=no
OP_COND=Default
FIX_GATED_CLOCKS=3
FIX_GENERATED_CLOCK=3
ADD_SPECIAL_LIBRARY_SOURCES=1
XILINX_92I_COMPATIBLE_MODE=0
USE_NCF_FOR_TIMING_CONSTRAINTS=0
ALTERA_MODELS=on
USE_XILINX_XFLOW=0
INCREMENTAL_FLOW=0
ENCHANCED_OPTIMIZATION=1
PMUXSLICE=1
HARDCOPY_DEVICE_OPTION=1
DOVERILOGHEADER=1
INSERT_IO_PADS=1
DISABLED_RESET=1
HARD_LIMIT_FANOUT=0
MAP_LOGIC=1
PERFORM_CLIQUING=1
SOFT_LCELLS=1
UPDATE_MODELS=0
VER_MODE=0
MODULAR=0
FORCE_RESET_PIN=1
CLOCK_FREQ=1
obtain_max_frequency=1
FANOUT_LIMIT=10000
FANIN_LIMIT=20
OPTIMIZE_PERCENT=0
MAX_TERMS=16
REPORT_PATH=4000
SYNTHESIS.USE_DEF_FANOUT=1
SYNTHESIS.USE_DEF_FANIN=1
SYMBOLIC_FSM=1
FSM_EXPLORER=0
FSM_ENCODE=default
RESOURCE_SHARING=1
RESULT_FORMAT=EDIF
ADD_SYS_LIB=0
CONSTRAINT_PATH=
PROPERTY_PATH=
SIMOUTFORM=2
AUTO_CLOSE_GUI=0
OVERRIDE_EXISTING_PROJECT=1
Retiming=0
Pipeline=1
VERILOG_LANGUAGE=SystemVerilog
VERILOG_COMPILER_DIRECTIVES=
PHYSICAL_SYNTHESIS=0
USE_TIMEQUEST_TIMING_ANALYZER=0
ENABLE_ADVANCED_LUT_COMBINING=1
COMPILE_WITH_DESIGNWARE_LIBRARY=0
FAST_SYNTHESIS=0
NETLIST_FORMAT=
POWERUP_VALUE_OF_A_REGISTER=0
QUARTUS_VERSION=Quartus II 7.2
PROMOTE_GLOBAL_BUFFER_THRESHOLD=50
NUMBER_OF_CRITICAL_PATHS=
NUMBER_OF_START_END_POINTS=
GENERATE_ISLAND_REPORT=1
PATH_PER_ISLAND=10
GROUP_RANGE=0.5
GLOBAL_RANGE=0.5
ENABLE_NETLIST_OPTIMIZATION=0
FEEDTHROUGH_OPTIMIZATION=0
CONSTANT_PROPAGATION=0
CREATE_LEVEL_HIERARCHY=0
CREATE_MAC_HIERARCHY=1
USE_CLOCK_PERIOD_FOR_UNCONSTRAINED_IO=0
ALLOW_DUPLICATE_MODULES=0
ANNOTATED_PROPERTIES_FOR_ANALYST=1
CONSERVATIVE_REGISTER_OPTIMIZATION=0
WRITE_VERIFICATION_INTERFACE_FORMAT_FILE=1
WRITE_VENDOR_CONSTRAINT_FILE=1
PUSH_TRISTATES=1
SYNTHESIS_ONOFF_IMPLEMENTED_AS_TRANSLATE_ONOFF=0
VHDL_2008=0
VENDOR_COMPATIBLE_MODE=0
DISABLE_SEQUENTIAL_OPTIMIZATIONS=0
HARDCOPY_II_DEVICE=
STRATIX_II_DEVICE=
STRATIX_II_SPEED=
NETLIST_RESTRUCTURE_FILES=
DESIGN_PLANS_FILES=
JOB_DESCRIPTION=SynthesisTask
SERVERFARM_INCLUDE_INPUT_FILES=*.*
SERVERFARM_EXCLUDE_INPUT_FILES=log\*.*:implement\*.*
JOB_SFM_RESOURCE=
LAST_RUN=1297366639

[PHYS_SYNTHESIS]
FAMILY=Xilinx11x SPARTAN3E
DEVICE=3s250etq144
SPEED=-5

[HierarchyViewer]
SortInfo=u
HierarchyInformation=
ShowHide=ShowTopLevel
Selected=

[Files]
[Files.Data]
'''


def read_build_yaml():
  build = yaml.load(file('../resource/build.yaml', 'r'))
  global gContentAdf
  config = ConfigParser.RawConfigParser(allow_no_value=True)
  config.optionxform = str
  config.readfp(io.BytesIO(gContentAdf))
  for key in build:
    for section in config.sections():
      try:
        config.get(section, key)
        config.set(section, key, build[key])
      except ConfigParser.NoOptionError:
        continue 
  return config, build

def gen_aws():
  content = '[Designs]\ndsn=./dsn.adf'
  f = open('../aldec/wsp.aws', 'w')
  f.write(content)
  f.close()
  
def gen_adf(iFilesMain, iFilesDep, iFilesTb, iConfig):
  main = ['/' + i + '=-1' for i in iFilesMain]
  dep  = ['dep/' + i + '=-1' for i in iFilesDep]
  tb   = ['TestBench/' + i + '=-1' for i in iFilesTb]
  src = '\n'.join(main+dep+tb)
  iConfig.set('Files', src)
  
  tb_data = ['.\\' + os.path.relpath(i)+'=Verilog Test Bench'
             for i in iFilesTb
             if os.path.splitext(i)[1] in ['.v']]
  src_data = '\n'.join(tb_data)
  iConfig.set('Files.Data', src_data)
  f = open('../aldec/dsn.adf', 'w')
  iConfig.write(f)
  f.close()


def gen_compile_cfg(iFiles):
  src = [] 
  for i in iFiles:
    try:
      res = '[file:.\\' + os.path.relpath(i) + ']\nEnabled=1'
    except ValueError:
      res = '[file:' + i + ']\nEnabled=1'
    src.append(res)
      
  content = '\n'.join(src)
  f = open('../aldec/compile.cfg', 'w')
  f.write(content)
  f.close()
  
def get_pattern_regexp(iBuild, iKey):
  pattern = iBuild.get(iKey, [])
  if iBuild.get('avhdl'):
    pattern_avhdl = iBuild.get('avhdl').get(iKey)
    if pattern_avhdl:
      pattern += pattern_avhdl 
  return pattern 


def export():
  if not os.path.exists('../aldec/src'):
    os.makedirs('../aldec/src')
  config, build = read_build_yaml()
  ignore = get_pattern_regexp(iBuild = build, iKey = 'ignore_regexp')
  only = get_pattern_regexp(iBuild = build, iKey = 'only_regexp')
  filesMain = structure.search(iPath = '../src', iIgnore = ignore, iOnly = only)
  filesDep = list(structure.getDepSrc(iSrc=filesMain, iIgnore = ignore, iOnly = only))
  filesTb = structure.search(iPath='../Testbench', iIgnore = ignore, iOnly = only)
  filesAll = filesMain + filesDep + filesTb

  build['src_main'] = filesMain
  build['src_dep']  = [str(i) for i in filesDep]
  build['src_tb']   = filesTb

  yaml.dump(build, open('../resource/build.yaml', 'w'), default_flow_style=False)
  
  gen_aws()
  gen_adf(iFilesMain=filesMain,
          iFilesDep=filesDep,
          iFilesTb=filesTb,
          iConfig=config)
  gen_compile_cfg(iFiles=filesAll)
    
  aldec = toolchain.getPath(iTag = 'avhdl_gui')
  subprocess.call(aldec+' ../aldec/wsp.aws')
  

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

      
#def export(iTopModule = '', iDsnName = '', iClean = False):
#  '''
#  Exports all design in Aldec.
#  '''
#  log.debug('def export IN iTopModule='+iTopModule+' iDsnName='+iDsnName+' iClean='+str(iClean))
#  dsn = structure.Design(iPath = '..', iInit = False)
#  if iDsnName:
#    dsnName = iDsnName
#  else:
#    dsnName = dsn.name
#  path = getPathTmp(dsn)
#  if iClean:
#    clean(path, dsnName)
##  gen_run(dsn)
#  log.info('Export done')
#  return dsn


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

  
  