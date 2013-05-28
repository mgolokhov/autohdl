import os
import shutil
import subprocess
import sys
import time

from autohdl import toolchain
from autohdl.hdlGlobals import implementPath
from autohdl.hdlLogger import log_call, logging
from autohdl import git
from time import strftime


log = logging.getLogger(__name__)


@log_call
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
        sys.exit()


@log_call
def clean(apath):
    if os.path.exists(apath):
        for root, dirs, files in os.walk(apath):
            for f in files:
                if os.path.splitext(f)[1] not in ['.mcs', '.bit']:
                    file_to_del = os.path.join(root, f)
                    try:
                        os.remove(file_to_del)
                    except OSError:
                        log.warning("Can't delete file " + file_to_del)
    if not os.path.exists(apath):
        os.makedirs(apath)


# TODO: that code should be in other place (git)
def copy_firmware(config):
    firmware_ext = ['.bit', '.mcs']
    dest_dir = os.path.join(config['hdlManager']['dsn_root'], 'resource')
    for i in os.listdir(dest_dir):
        if os.path.splitext(i)[1] in firmware_ext:
            log.info('removing ' + os.path.join(dest_dir, i))
            os.remove(os.path.join(dest_dir, i))

    for i in firmware_ext:
        src_abs_path = os.path.join(config['hdlManager']['dsn_root'],
                                    'autohdl/implement',
                                    config['hdlManager'].get('top'),
                                    config['hdlManager'].get('top') + i)
        if os.path.exists(src_abs_path):
            dest = '{dsn}_{top}_build_{ver}{ext}'.format(
                dsn=os.path.basename(os.path.abspath('..')),
                top=config['hdlManager'].get('top'),
                ver=strftime('%y%m%d_%H%M%S', time.localtime()),
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

#project set "FPGA Start-Up Clock" "JTAG Clock"

{xfiles}

project set top "{top}"

{process_run}

project close
"""


def clean_project(config):
    if os.path.exists(config['xilinx']['project_directory']):
        try:
            shutil.rmtree(config['xilinx']['project_directory'])
        except Exception as e:
            log.warning(e)


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
    config['execution_fifo'] = list()
    run = '{program} {arguments}'.format(program=toolchain.Tool().get('ise_batch'),
                                         arguments=config['xilinx']['script_path'])
    config['execution_fifo'].append(run)
    if config['hdlManager']['cl']['xilinx'] == 'gui-clean' or config['hdlManager']['cl']['xilinx'] == 'gui':
        config['xilinx']['project_file'] = os.path.join(config['xilinx']['project_directory'],
                                                        config['hdlManager']['top'] + '.xise')
        run = '{program} {arguments}'.format(program=toolchain.Tool().get('ise_gui'),
                                             arguments=config['xilinx']['project_file'])
        config['execution_fifo'].append(run)
    if config['hdlManager'].get('debug') != 'hardcore_test':
        for i in config['execution_fifo']:
            p = subprocess.Popen(i, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            while True:
                out = p.stdout.read(1)
                if out == "" or p.poll() is not None:
                    break
                else:
                    sys.stdout.write(out)
                    sys.stdout.flush()


def run_project(config):
    config['xilinx'] = dict()
    config['xilinx']['project_directory'] = os.path.abspath(os.path.join('..',
                                                                         'autohdl',
                                                                         'implement',
                                                                         config['hdlManager']['top']))
    # check project.tcl src files if they are not modified, don't clean
    clean_project(config)

    if not os.path.exists(config['xilinx']['project_directory']):
        os.makedirs(config['xilinx']['project_directory'])
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
    if not os.path.exists(synthesis_result_constraint):
        print 'cant find', synthesis_result_constraint
        synthesis_result_constraint = config['hdlManager']['ucf']
    if not os.path.exists(synthesis_result_constraint):
        log.warning('No constraint file')
    netlists = config['structure'].get('netlists') or []  # should type list
    impl_src = set()
    impl_src.add(synthesis_result_constraint)
    impl_src.add(synthesis_result_netlist)
    for i in netlists:
        impl_src.add(i)

    config['xilinx']['src'] = impl_src
    return impl_src




