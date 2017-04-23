import os
import pprint



def synth_tool(iPrj):
    return 'MV_SYNPLIFY_PREMIER_C2009_06'


def impl_tool(iPrj):
    return 'MV_ISE111'


def family(iPrj):
    family = (iPrj.get('technology') or
              'Xilinx11x SPARTAN3E')
    return family


def device(iPrj):
    device = (iPrj.get('part')+iPrj.get('package') or
              '3s1200efg320')
    return device


def toplevel(iPrj):
    toplevel = iPrj.get('top_module')
    return toplevel


def ucf(iPrj):
    ucf = (
        iPrj.get('ucf')
        )
    return ucf


def include_path(iPrj):
    incl_path = iPrj.get('include_path')
    if not incl_path:
        return ''
    elif type(incl_path) is str:
        incl_path = [incl_path]
    counter = 'Count={0}'.format(len(incl_path))
    inclDir = ['IncludeDir{0}={1}'.format(i, path) for i, path in enumerate(incl_path)]
    return '{0}\n{1}'.format(counter, '\n'.join(inclDir))


def files(config):
    virt_dirs = {'deps=1'}
    virt_paths = []

    for i in config['aldec']['dsn_src']:
        virt_dir = os.path.dirname(i).replace('/', '\\').replace(config['aldec']['wsp_root']+'\\', '')
        if virt_dir != config['aldec']['wsp_root']:
            virt_dirs.add(virt_dir+'=1')
        virt_paths.append(virt_dir + '/' + i + '=-1')
    # pprint.pprint(virt_dirs)
    # pprint.pprint(virt_paths)
    # import sys; sys.exit(0);

    if config['aldec'].get('deps'):
        virt_paths += ['deps/' + i + '=-1' for i in config['aldec'].get('deps')]

    # pprint.pprint(virt_dirs)
    # pprint.pprint(virt_paths)
    # import sys; sys.exit(0);

    for i in config['aldec']['all_src']:
        virt_dir = 'all\\' + os.path.dirname(i).replace(config['aldec']['wsp_root']+'\\', '')
        if virt_dir != 'all\\' + config['aldec']['wsp_root']:
            virt_dirs.add(virt_dir + '=1')
        else:
            virt_dir = "all/"

        p = os.path.join(config['dsn_root'], 'autohdl')
        r = os.path.relpath(i, p)
        f = '\\..\\' * (len((virt_dir.split('\\')))) + r

        virt_paths.append(virt_dir + '/' + i + '=-1')
        # if 'doit.sublime-project' in i:
        #     print(config['aldec']['wsp_root'])
        #     pprint.pprint(virt_dirs)
        #     pprint.pprint(virt_paths)
        #     import sys; sys.exit(0);

    config['aldec']['virt_dirs'] = virt_dirs
    config['aldec']['virt_paths'] = virt_paths


def files_data(iPrj):
    #import pprint
    #pprint.pprint(iPrj['aldec']['TestBenchSrc'])
    srcTb = ['.\\' + os.path.relpath(i) + '=Verilog Test Bench'
             for i in iPrj['aldec']['TestBenchSrc']
             if os.path.splitext(i)[1] in ['.v']]
    filesData = '\n'.join(srcTb)
    return filesData


def defineMacro(iPrj):
    macros = ""#iPrj.get('hdlManager').get('AldecMacros')
    #print(macros)
    if macros:
        return '[DefineMacro]\nGlobal=' + ' '.join(macros) + '\n'
    else:
        return ''


def generate(iPrj):
    files(iPrj)
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

                + 'SYNTH_TOOL={SYNTH_TOOL}\n'.format(SYNTH_TOOL=synth_tool(iPrj)) +
                'RUN_MODE_SYNTH=1\n'
                + 'IMPL_TOOL={IMPL_TOOL}\n'.format(IMPL_TOOL=impl_tool(iPrj)) +
                'CSYNTH_TOOL=<none>\n'
                'PHYSSYNTH_TOOL=<none>\n'
                'FLOWTOOLS=IMPL_WITH_SYNTH\n'
                'ON_SERVERFARM_SYNTH=0\n'
                'ON_SERVERFARM_IMPL=0\n'
                'ON_SERVERFARM_SIM=0\n'
                'DVM_DISPLAY=NO\n'
                'VerilogDirsChanged=1\n'
                + 'FAMILY={FAMILY}\n'.format(FAMILY=family(iPrj)) +
                'SYNTH_STATUS=none\n'
                'IMPL_STATUS=none\n'
                'RUN_MODE_IMPL=0\n'


                '[IMPLEMENTATION]\n'
                'FLOW_STEPS_RESET=0\n'
                + 'UCF={UCF}\n'.format(UCF=ucf(iPrj)) +
                'DEVICE_TECHNOLOGY_MIGRATION_LIST=\n'
                + 'FAMILY={FAMILY}\n'.format(FAMILY=family(iPrj))
                + 'DEVICE={DEVICE}\n'.format(DEVICE=device(iPrj)) +
                'SPEED=-5\n'
                'IS_BAT_MODE=0\n'
                'BAT_FILE=\n'
                'NETLIST=\n'
                'DEF_UCF=2\n'
                + 'OLD_FAMILY={FAMILY}\n'.format(FAMILY=family(iPrj)) +
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
                + 'TOPLEVEL={TOPLEVEL}\n'.format(TOPLEVEL=toplevel(iPrj))
                + 'FAMILY={FAMILY}\n'.format(FAMILY=family)
                + 'OLD_FAMILY={FAMILY}\n'.format(FAMILY=family(iPrj))
                + 'DEVICE={DEVICE}\n'.format(DEVICE=device(iPrj)) +
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
                + 'FAMILY={FAMILY}\n'.format(FAMILY=family(iPrj))
                + 'DEVICE={DEVICE}\n'.format(DEVICE=device(iPrj)) +
                'SPEED=-5\n'

                '[HierarchyViewer]\n'
                'SortInfo=u\n'
                'HierarchyInformation=\n'
                'ShowHide=ShowTopLevel\n'
                'Selected=\n'

                '[Verilog Library]\n'
                # should be installed
                'xilinxcorelib_ver=\n'
                'unisims_ver=\n'
                'unimacro_ver=\n'
                'simprimps_ver=\n'
                # 'ovi_xilinxcorelib=\n'
                # 'ovi_unisim=\n'

                '[LocalVerilogSets]\n'
                # SystemVerilog 1800-2012
                'VerilogLanguage=8\n'

                '[LocalVerilogDirs]\n'
                + '{LocalVerilogDirs}\n'.format(LocalVerilogDirs=include_path(iPrj)) +

                defineMacro(iPrj) +


                '[Groups]\n'
                + '{groups}\n'.format(groups='\n'.join(iPrj['aldec']['virt_dirs'])) +

                '[Files]\n'
                + '{Files}\n'.format(Files='\n'.join(iPrj['aldec']['virt_paths'])) +

                '[Files.Data]\n'
                #'{Files_Data}\n'.format(Files_Data=files_data(iPrj))
        )

    return template

if __name__ == '__main__':
    generate({'build': {}})