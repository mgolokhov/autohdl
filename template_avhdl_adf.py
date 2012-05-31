import os

# every func should return a string


def synth_tool(iPrj):
#  return 'MV_SYNPLIFY_PREMIER_D2010_03'
  return 'MV_SYNPLIFY_PREMIER_C2009_06'


def impl_tool(iPrj):
  return 'MV_ISE111'


def family(iPrj):
  family = (iPrj['build'].get('family') or
            iPrj['build'].get('FAMILY') or
            'Xilinx11x SPARTAN3E')
  return family

def device(iPrj):
  device = (iPrj['build'].get('device') or
            iPrj['build'].get('DEVICE') or
            '3s1200efg320')
  return device

def toplevel(iPrj):
  toplevel = (iPrj['build'].get('toplevel') or
              iPrj['build'].get('TOPLEVEL')
              )
  return toplevel

def ucf(iPrj):
  ucf = (
    iPrj['build'].get('ucf') or
    iPrj['build'].get('UCF')
  )
  return ucf


def include_path(iPrj):
  incl_path = iPrj['build'].get('include_path')
  if not incl_path:
    return ''
  counter = 'Count={0}'.format(len(incl_path))
  inclDir = ['IncludeDir{0}={1}'.format(i, path) for i, path in enumerate(incl_path)]
  return '{0}\n{1}'.format(counter, '\n'.join(inclDir))

def files(iPrj):

  dep = []
  if iPrj.get('depSrc'):
    iPrj['depSrc'].sort(key=str.lower)
    dep  = ['dep/' + i + '=-1' for i in iPrj['depSrc']]

  rootPath = iPrj['repoPath']+'/'
  l = []
  # relative path to aldec/src/virtualDirectory
  for i in iPrj['repoSrc']:
    virtFolder = os.path.dirname(i).replace('\\', '/').split(rootPath)[1]
    virtFolder = virtFolder.replace('/', '\\').rstrip('/src')
    ass = len(virtFolder.split('\\')) + 1 # counts repo dir
    l.append('repo\\' + virtFolder +'/..'*ass + '/../../script/' + os.path.relpath(i) + '=-1')
  repo = l


  netlist = []
#  if iPrj.get('netlistSrc'):
#    iPrj['netlistSrc'].sort()
#    netlist = ['/'+ i + '=-1' for i in iPrj['netlistSrc']]

  uncopied = []
  if iPrj.get('srcUncopied'):
    iPrj['srcUncopied'].sort()
    uncopied = ['/'+ i + '=-1' for i in iPrj['srcUncopied']]

  allOtherSrc = list(set(iPrj['allSrc']) - set(iPrj['depSrc']))
  if allOtherSrc:
    allOtherSrc.sort(key=str.lower)
  rootPath = iPrj['rootPath']+'/'
  l = []
  for i in allOtherSrc:
    virtFolder = os.path.dirname(i).replace('\\', '/').split(rootPath)[1]
    virtFolder = virtFolder.replace('/', '\\')
    l.append(virtFolder + '/' + i + '=-1')
  allOtherSrc = l
  files = '\n'.join(dep + netlist + allOtherSrc + uncopied + repo)
  return files


def files_data(iPrj):
  srcTb = ['.\\' + os.path.relpath(i) + '=Verilog Test Bench'
            for i in iPrj['TestBenchSrc']
            if os.path.splitext(i)[1] in ['.v']]
  filesData = '\n'.join(srcTb)
  return filesData


def generate(iPrj):
  template = ('\n'
  '[Project]\n'
  'Current Flow=Multivendor\n'
  'VCS=0\n'
  'version=3\n'
  'Current Config=compilen\n'
  
  '[Settings]\n'
  'AccessRead=0\n'
  'AccessReadWrite=0\n'
  'AccessACCB=0\n'
  'AccessACCR=0\n'
  'AccessReadWriteSLP=0\n'
  'AccessReadTopLevel=1\n'
  'DisableC=1\n'
  'ENABLE_ADV_DATAFLOW=0\n'
  'FLOW_TYPE=HDL\n'
  'LANGUAGE=VERILOG\n'
  'REFRESH_FLOW=1\n'
  +'SYNTH_TOOL={SYNTH_TOOL}\n'.format(SYNTH_TOOL = synth_tool(iPrj))+
  'RUN_MODE_SYNTH=1\n'
  +'IMPL_TOOL={IMPL_TOOL}\n'.format(IMPL_TOOL = impl_tool(iPrj))+
  'CSYNTH_TOOL=<none>\n'
  'PHYSSYNTH_TOOL=<none>\n'
  'FLOWTOOLS=IMPL_WITH_SYNTH\n'
  'ON_SERVERFARM_SYNTH=0\n'
  'ON_SERVERFARM_IMPL=0\n'
  'ON_SERVERFARM_SIM=0\n'
  'DVM_DISPLAY=NO\n'
  'VerilogDirsChanged=1\n'
  +'FAMILY={FAMILY}\n'.format(FAMILY = family(iPrj))+
  'SYNTH_STATUS=none\n'
  'IMPL_STATUS=none\n'
  'RUN_MODE_IMPL=0\n'
  
  
  '[IMPLEMENTATION]\n'
  'FLOW_STEPS_RESET=0\n'
  +'UCF={UCF}\n'.format(UCF=ucf(iPrj))+
  'DEVICE_TECHNOLOGY_MIGRATION_LIST=\n'
  +'FAMILY={FAMILY}\n'.format(FAMILY=family(iPrj))
  +'DEVICE={DEVICE}\n'.format(DEVICE=device(iPrj))+
  'SPEED=-5\n'
  'IS_BAT_MODE=0\n'
  'BAT_FILE=\n'
  'NETLIST=\n'
  'DEF_UCF=2\n'
  +'OLD_FAMILY={FAMILY}\n'.format(FAMILY=family(iPrj))+
  'wasChanged_Change_Device_Speed=0\n'
  'wasChanged_Change_Device_Speed_To=0\n'
  'wasChanged_Change_Device_Speed_To2=0\n'
  'Place_And_Route_Mode_old_value=Normal\n'
  'JOB_DESCRIPTION=ImplementationTask\n'
  'SERVERFARM_INCLUDE_INPUT_FILES=*.*\n'
  'SERVERFARM_EXCLUDE_INPUT_FILES=log\*.*\n'
  'JOB_SFM_RESOURCE=\n'
  'SYNTH_TOOL_RESET=0\n'
  
  '[SYNTHESIS]\n'
  'DEVICE_SET_FLAG=1\n'
  'OBSOLETE_ALIASES=1\n'
  'VIEW_MODE=RTL\n'
  +'TOPLEVEL={TOPLEVEL}\n'.format(TOPLEVEL=toplevel(iPrj))
  +'FAMILY={FAMILY}\n'.format(FAMILY=family)
  +'OLD_FAMILY={FAMILY}\n'.format(FAMILY=family(iPrj))
  +'DEVICE={DEVICE}\n'.format(DEVICE=device(iPrj))+
  'SPEED=-5\n'
  'ADDITIONAL_OPTIONS_ON_STARTUP=\n'
  'FORCE_GSR=no\n'
  'OP_COND=Default\n'
  'FIX_GATED_CLOCKS=3\n'
  'FIX_GENERATED_CLOCK=3\n'
  'ADD_SPECIAL_LIBRARY_SOURCES=1\n'
  'XILINX_92I_COMPATIBLE_MODE=0\n'
  'USE_NCF_FOR_TIMING_CONSTRAINTS=0\n'
  'ALTERA_MODELS=on\n'
  'USE_XILINX_XFLOW=0\n'
  'INCREMENTAL_FLOW=0\n'
  'ENCHANCED_OPTIMIZATION=1\n'
  'PMUXSLICE=1\n'
  'HARDCOPY_DEVICE_OPTION=1\n'
  'DOVERILOGHEADER=1\n'
  'INSERT_IO_PADS=1\n'
  'DISABLED_RESET=1\n'
  'HARD_LIMIT_FANOUT=0\n'
  'MAP_LOGIC=1\n'
  'PERFORM_CLIQUING=1\n'
  'SOFT_LCELLS=1\n'
  'UPDATE_MODELS=0\n'
  'VER_MODE=0\n'
  'MODULAR=0\n'
  'FORCE_RESET_PIN=1\n'
  'CLOCK_FREQ=1\n'
  'obtain_max_frequency=1\n'
  'FANOUT_LIMIT=10000\n'
  'FANIN_LIMIT=20\n'
  'OPTIMIZE_PERCENT=0\n'
  'MAX_TERMS=16\n'
  'REPORT_PATH=4000\n'
  'SYNTHESIS.USE_DEF_FANOUT=1\n'
  'SYNTHESIS.USE_DEF_FANIN=1\n'
  'SYMBOLIC_FSM=1\n'
  'FSM_EXPLORER=0\n'
  'FSM_ENCODE=default\n'
  'RESOURCE_SHARING=1\n'
  'RESULT_FORMAT=EDIF\n'
  'ADD_SYS_LIB=0\n'
  'CONSTRAINT_PATH=\n'
  'PROPERTY_PATH=\n'
  'SIMOUTFORM=2\n'
  'AUTO_CLOSE_GUI=0\n'
  'OVERRIDE_EXISTING_PROJECT=1\n'
  'Retiming=0\n'
  'Pipeline=1\n'
  'VERILOG_LANGUAGE=SystemVerilog\n'
  'VERILOG_COMPILER_DIRECTIVES=\n'
  'PHYSICAL_SYNTHESIS=0\n'
  'USE_TIMEQUEST_TIMING_ANALYZER=0\n'
  'ENABLE_ADVANCED_LUT_COMBINING=1\n'
  'COMPILE_WITH_DESIGNWARE_LIBRARY=0\n'
  'FAST_SYNTHESIS=0\n'
  'NETLIST_FORMAT=\n'
  'POWERUP_VALUE_OF_A_REGISTER=0\n'
  'QUARTUS_VERSION=Quartus II 7.2\n'
  'PROMOTE_GLOBAL_BUFFER_THRESHOLD=50\n'
  'NUMBER_OF_CRITICAL_PATHS=\n'
  'NUMBER_OF_START_END_POINTS=\n'
  'GENERATE_ISLAND_REPORT=1\n'
  'PATH_PER_ISLAND=10\n'
  'GROUP_RANGE=0.5\n'
  'GLOBAL_RANGE=0.5\n'
  'ENABLE_NETLIST_OPTIMIZATION=0\n'
  'FEEDTHROUGH_OPTIMIZATION=0\n'
  'CONSTANT_PROPAGATION=0\n'
  'CREATE_LEVEL_HIERARCHY=0\n'
  'CREATE_MAC_HIERARCHY=1\n'
  'USE_CLOCK_PERIOD_FOR_UNCONSTRAINED_IO=0\n'
  'ALLOW_DUPLICATE_MODULES=0\n'
  'ANNOTATED_PROPERTIES_FOR_ANALYST=1\n'
  'CONSERVATIVE_REGISTER_OPTIMIZATION=0\n'
  'WRITE_VERIFICATION_INTERFACE_FORMAT_FILE=1\n'
  'WRITE_VENDOR_CONSTRAINT_FILE=1\n'
  'PUSH_TRISTATES=1\n'
  'SYNTHESIS_ONOFF_IMPLEMENTED_AS_TRANSLATE_ONOFF=0\n'
  'VHDL_2008=0\n'
  'VENDOR_COMPATIBLE_MODE=0\n'
  'DISABLE_SEQUENTIAL_OPTIMIZATIONS=0\n'
  'HARDCOPY_II_DEVICE=\n'
  'STRATIX_II_DEVICE=\n'
  'STRATIX_II_SPEED=\n'
  'NETLIST_RESTRUCTURE_FILES=\n'
  'DESIGN_PLANS_FILES=\n'
  'JOB_DESCRIPTION=SynthesisTask\n'
  'SERVERFARM_INCLUDE_INPUT_FILES=*.*\n'
  'SERVERFARM_EXCLUDE_INPUT_FILES=log\*.*:implement\*.*\n'
  'JOB_SFM_RESOURCE=\n'
  'LAST_RUN=1297366639\n'
  
  '[PHYS_SYNTHESIS]\n'
  +'FAMILY={FAMILY}\n'.format(FAMILY=family(iPrj))
  +'DEVICE={DEVICE}\n'.format(DEVICE=device(iPrj))+
  'SPEED=-5\n'
  
  '[HierarchyViewer]\n'
  'SortInfo=u\n'
  'HierarchyInformation=\n'
  'ShowHide=ShowTopLevel\n'
  'Selected=\n'
  
  '[Verilog Library]\n'
  # should be installed
  'ovi_xilinxcorelib=\n'
  'ovi_unisim=\n'
  
  '[LocalVerilogSets]\n'
  # SystemVerilog 1800-2005
  'VerilogLanguage=7\n'
  
  '[LocalVerilogDirs]\n'
  +'{LocalVerilogDirs}\n'.format(LocalVerilogDirs=include_path(iPrj)) +
  
  '[Groups]\n'
  'src=1\n'
  'dep=1\n'
  'script=1\n'
  'resource=1\n'
  'TestBench=1\n'
  'repo\n'
  
  '[Files]\n'
  +'{Files}\n'.format(Files=files(iPrj))+
  
  '[Files.Data]\n'
  '{Files_Data}\n'.format(Files_Data=files_data(iPrj))
  )

  return template

if __name__ == '__main__':
  generate({'build':{}})