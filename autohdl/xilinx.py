import os
import shutil
import subprocess
import sys
import time
from time import strftime

from autohdl import toolchain
from autohdl.hdlLogger import log_call, logging


log = logging.getLogger(__name__)


#@log_call
def bit2mcs(config):
    try:
        if config['hdlManager']['size']:
            proc = '{tool} -u 0 {top} -s {size} -w'.format(tool=toolchain.Tool().get('ise_promgen'),
                                                           top=os.path.join(config['hdlManager']['dsn_root'],
                                                                            'autohdl',
                                                                            'implement',
                                                                            config['hdlManager']['top'],
                                                                            config['hdlManager']['top'] + '.bit'),
                                                           size=config['hdlManager']['size'])
            subprocess.check_call(proc)
        else:
            log.warning('PROM size was not set')
    except subprocess.CalledProcessError as e:
        log.error(e)
        sys.exit(1)


def copy_firmware(config):
    firmware_ext = ['.bit', '.mcs']
    build_timestamp = strftime('%y%m%d_%H%M%S', time.localtime())
    dest_dirs = [os.path.join(config['hdlManager']['dsn_root'], 'resource'),
                 os.path.join(config['hdlManager']['dsn_root'], 'autohdl', 'firmware')]
    for dest_dir in dest_dirs:
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        dest = '{dsn}_{top}_build_'.format(
            dsn=os.path.basename(os.path.abspath('..')),
            top=config['hdlManager'].get('top'))
        for i in os.listdir(dest_dir):
            if os.path.splitext(i)[1] in firmware_ext and dest in i:
                log.info('removing ' + os.path.join(dest_dir, i))
                try:
                    os.remove(os.path.join(dest_dir, i))
                except Exception as e:
                    log.warning(e)

        for i in firmware_ext:
            src_abs_path = os.path.join(config['hdlManager']['dsn_root'],
                                        'autohdl/implement',
                                        config['hdlManager'].get('top'),
                                        config['hdlManager'].get('top') + i)
            if os.path.exists(src_abs_path):
                dest = '{dsn}_{top}_build_{ver}{ext}'.format(
                    dsn=os.path.basename(os.path.abspath('..')),
                    top=config['hdlManager'].get('top'),
                    ver=build_timestamp,
                    ext=i
                )
                dest_abs_path = os.path.join(dest_dir, dest)
                log.info('copying ' + dest_abs_path)
                shutil.copy(src_abs_path, dest_abs_path)




xtcl_script = """
project new {project_name}.xise

project set family "{family}"
project set device "{device}"
project set package "{package}"
project set speed "{speed}"

project set top_level_module_type "EDIF"
project set "Preferred Language" "Verilog"
project set "Verilog Macros" "I_HAVE_ONLY_FUCKING_XST"
#project set "FPGA Start-Up Clock" "JTAG Clock"

{xfiles}

project set top "{top}"

{process_run}

project close
"""


def clean(config):
    for i in range(3):
        if os.path.exists(config['xilinx']['project_directory']):
            try:
                shutil.rmtree(config['xilinx']['project_directory'])
                break
            except Exception as e:
                log.warning(e)
    if os.path.exists(config['xilinx']['project_directory']):
        message = 'Cant clean xilinx project '+config['xilinx']['project_directory']
        log.error(message)
        sys.exit(message)


def mk_new(config):
    for i in range(3):
        if not os.path.exists(config['xilinx']['project_directory']):
            try:
                os.makedirs(config['xilinx']['project_directory'])
                break
            except Exception as e:
                log.warning(e)
                time.sleep(1)
    if not os.path.exists(config['xilinx']['project_directory']):
        message = 'Cant make xilinx project '+config['xilinx']['project_directory']
        log.error(message)
        sys.exit(message)


def mk_project_script(config):
    xfiles = ['xfile add "{}"'.format(afile.replace('\\', '/')) for afile in form_project_src(config)]
    project_name = os.path.abspath(os.path.join('..',
                                                'autohdl',
                                                'implement',
                                                config['hdlManager']['top'],
                                                config['hdlManager']['top']))
    project_name = project_name.replace('\\', '/')
    gen_prog_file = (config['hdlManager']['cl']['xilinx'] == 'batch')
    res = xtcl_script.format(
        project_name=project_name,
        family=config['hdlManager']['technology'],
        device=config['hdlManager']['part'],
        package=config['hdlManager']['package'],
        speed=config['hdlManager']['speed_grade'],
        xfiles='\n'.join(xfiles),
        top=config['hdlManager']['top'],
        process_run='process run "Generate Programming File"' if gen_prog_file else ""
    )

    with open(config['xilinx']['script_path'], 'w') as f:
        f.write(res)


def run_shit(config):
    execution_fifo = []
    first_run = '{program} {arguments}'.format(program=toolchain.Tool().get('ise_batch'),
                                               arguments=config['xilinx']['script_path'])

    execution_fifo.append(first_run)
    is_gui_mode = (config['hdlManager']['cl']['xilinx'] == 'gui-clean' or
                   config['hdlManager']['cl']['xilinx'] == 'gui')
    if is_gui_mode:
        config['xilinx']['project_file'] = os.path.join(config['xilinx']['project_directory'],
                                                        config['hdlManager']['top'] + '.xise')
        second_run = '{program} {arguments}'.format(program=toolchain.Tool().get('ise_gui'),
                                                    arguments=config['xilinx']['project_file'])
        execution_fifo.append(second_run)
    if not config.get('TDD'):
        for i in execution_fifo:
            if subprocess.call(i):
                message = 'Error to run: '+first_run
                log.error(message)
                sys.exit(message)
    else:
        config['tdd']['execution_fifo'] = execution_fifo


def run_project(config):
    config['xilinx'] = dict()
    config['xilinx']['project_directory'] = os.path.abspath(os.path.join('..',
                                                                         'autohdl',
                                                                         'implement',
                                                                         config['hdlManager']['top']))
    # TODO: check project.tcl src files if they are not modified, don't clean
    clean(config)
    mk_new(config)

    config['xilinx']['script_path'] = os.path.abspath(os.path.join('..',
                                                                   'autohdl',
                                                                   'implement',
                                                                   config['hdlManager']['top'],
                                                                   config['hdlManager']['top'] + '.tcl'))
    if not os.path.exists(config['xilinx']['script_path']):
        mk_project_script(config)

    run_shit(config)
    # copy_firmware(config)


def form_project_src(config):
    """
     return a list of source files as absolute paths
    """
    impl_src = set()
    if True: #config.get('synthesis') == 'synplify':
        synthesis_result_netlist = os.path.abspath(os.path.join('..',
                                                                'autohdl',
                                                                'synthesis',
                                                                config['hdlManager']['top'],
                                                                config['hdlManager']['top'] + '.edf', ))
        log.info('Searching a netlist after synplify')
        for i in range(30):
            print "."
            if os.path.exists(synthesis_result_netlist):
                break
            time.sleep(0.5)
        if not os.path.exists(synthesis_result_netlist):
            log.error('Cannot find netlist. Try synthesis first.')
            sys.exit(1)

        synthesis_result_constraint = os.path.abspath(os.path.join('..',
                                                                   'autohdl',
                                                                   'synthesis',
                                                                   config['hdlManager']['top'],
                                                                   'synplicity.ucf', ))
        impl_src.add(synthesis_result_netlist)
        if not os.path.exists(synthesis_result_constraint):
            print 'cant find', synthesis_result_constraint
            synthesis_result_constraint = config['hdlManager']['ucf']
        if not os.path.exists(synthesis_result_constraint):
            log.warning('No constraint file')
    else:
        synthesis_result_constraint = config['hdlManager']['ucf']
        for i in config['structure']['mainSrc']+config['structure']['depSrc']:
            impl_src.add(i)
    impl_src.add(synthesis_result_constraint)
    netlists = config['structure'].get('netlists') or []  # should type list
    for i in netlists:
        impl_src.add(i)


    config['xilinx']['src'] = impl_src
    return impl_src




