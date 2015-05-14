import os
import shutil
import subprocess
import sys
import time
from time import strftime
import locale
import copy

from autohdl import toolchain
from autohdl.hdl_logger import logging
from autohdl.hdl_globals import IMPLEMENT_PATH, SYNTHESIS_PATH, NETLIST_EXT


log = logging.getLogger(__name__)


XTCL_SCRIPT = """\
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

PROCESS_WITH_HANDLER = '''\
process run "Generate Programming File"

set my_status [ process get "Generate Programming File" status ]
puts $my_status
if {( $my_status == "up_to_date" ) ||
    ( $my_status == "warnings" ) } {
     puts "Process Ok"
} else {
    puts "Process failed"
    exit 1
}
'''


def bit_to_mcs(cfg):
    extend_cfg(cfg)
    try:
        if ['eeprom_kilobytes']:
            proc = '{tool} -u 0 {top} -s {size} -w'.format(tool=toolchain.Tool().get('ise_promgen'),
                                                           top=cfg['bit_file'],
                                                           size=cfg['eeprom_kilobytes'])
            subprocess.check_call(proc)
        else:
            log.warning('EEPROM size was not set')
    except subprocess.CalledProcessError as e:
        log.error(e)
        sys.exit(1)


def copy_firmware(cfg):
    firmware_ext = ['.bit', '.mcs']
    build_timestamp = strftime('%y%m%d_%H%M%S', time.localtime())
    dest_dirs = [os.path.join('..', 'resource'),
                 os.path.join('..', 'autohdl', 'firmware')]
    for dest_dir in dest_dirs:
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        dest = '{dsn}_{top}_'.format(dsn=os.path.basename(os.path.abspath('..')),
                                           top=cfg.get('top_module'))
        for i in os.listdir(dest_dir):
            if os.path.splitext(i)[1] in firmware_ext and dest in i:
                log.info('removing ' + os.path.join(dest_dir, i))
                try:
                    os.remove(os.path.join(dest_dir, i))
                except Exception as e:
                    log.warning(e)

        for i in firmware_ext:
            src_abs_path = os.path.join('..',
                                        'autohdl/implement',
                                        cfg.get('top_module'),
                                        cfg.get('top_module') + i)
            if os.path.exists(src_abs_path):
                dest = '{dsn}_{top}_{ver}{ext}'.format(
                    dsn=os.path.basename(os.path.abspath('..')),
                    top=cfg.get('top_module'),
                    ver=build_timestamp,
                    ext=i
                )
                dest_abs_path = os.path.join(dest_dir, dest)
                log.info('copying ' + dest_abs_path)
                shutil.copy(src_abs_path, dest_abs_path)


def clean(cfg):
    for i in range(3):
        if os.path.exists(cfg['prj_dir']):
            try:
                shutil.rmtree(cfg['prj_dir'])
                break
            except Exception as e:
                log.warning(e)
                time.sleep(1)
    if os.path.exists(cfg['prj_dir']):
        message = "Can't clean xilinx project {}".format(cfg['prj_dir'])
        log.error(message)
        sys.exit(message)


def mk_dir(cfg):
    for i in range(3):
        if not os.path.exists(cfg['prj_dir']):
            try:
                os.makedirs(cfg['prj_dir'])
                break
            except Exception as e:
                log.warning(e)
                time.sleep(1)
    if not os.path.exists(cfg['prj_dir']):
        message = "Can't make xilinx project {}".format(cfg['prj_dir'])
        log.error(message)
        sys.exit(message)


def mk_script(cfg):
    src = [i.replace('\\', '/') for i in cfg['src'] if os.path.splitext(i)[1] in NETLIST_EXT]
    # should be copied after synplify
    src.append(cfg['syn_constraint'])
    src.append(cfg['syn_netlist'])
    xfiles = ['xfile add "{}"'.format(afile.replace('\\', '/')) for afile in src]
    if cfg['xilinx'] == 'batch':
        proc_run = PROCESS_WITH_HANDLER
    else:  # gui mode, just generate .xise file at first
        proc_run = ""
    res = XTCL_SCRIPT.format(project_name=cfg['prj_name'],
                             family=cfg['technology'],
                             device=cfg['part'],
                             package=cfg['package'],
                             speed=cfg['speed_grade'],
                             xfiles='\n'.join(xfiles),
                             top=cfg['top_module'],
                             process_run=proc_run
                             )

    with open(cfg['prj_script'], 'w') as f:
        f.write(res)


def run_tool(cfg):
    # if gui mode just generate gui project file
    command = '{program} {arguments}'.format(program=toolchain.Tool().get('ise_batch'),
                                             arguments=cfg['prj_script'])
    subprocess.check_call(command)
    if cfg['xilinx'] == 'gui':
        command = '{program} {arguments}'.format(program=toolchain.Tool().get('ise_gui'),
                                                 arguments=cfg['prj_gui_file'])
        subprocess.check_call(command)


def load_env_settings():
    try:
        wrapper = toolchain.Tool().get('ise_wrapper')
        print(wrapper)
        encoding = locale.getdefaultlocale()[1]
        res = subprocess.check_output('cmd /c "call {0} & set"'.format(wrapper.replace('/', '\\')))
        res = res.decode(encoding)
        d = {}
        #create key=value environment variables
        for i in res.split(os.linesep):
            res = i.split('=')
            if len(res) == 2:
                d.update({res[0]: res[1]})
        return d
    except Exception as exp:
        log.error(exp)


def extend_cfg(cfg):
    cfg['prj_dir'] = os.path.abspath(os.path.join(IMPLEMENT_PATH, cfg['top_module'])).replace('\\', '/')
    cfg['prj_name'] = os.path.join(cfg['prj_dir'], cfg['top_module']).replace('\\', '/')
    cfg['prj_script'] = os.path.abspath(os.path.join(cfg['prj_dir'], cfg['top_module']+'.tcl')).replace('\\', '/')
    cfg['syn_netlist'] = os.path.abspath(os.path.join(SYNTHESIS_PATH, cfg['top_module'], cfg['top_module']+'.edf')).replace('\\', '/')
    cfg['syn_constraint'] = os.path.abspath(os.path.join(SYNTHESIS_PATH, cfg['top_module'], 'synplicity.ucf')).replace('\\', '/')
    # for gui mode
    cfg['prj_gui_file'] = os.path.abspath(os.path.join(cfg['prj_dir'], cfg['top_module'] + '.xise')).replace('\\', '/')
    cfg['bit_file'] = os.path.abspath(os.path.join(cfg['prj_dir'], cfg['top_module']+'.bit')).replace('\\', '/')


def run(cfg):
    # TODO: check project.tcl src files if they are not modified, don't clean
    cfg = copy.deepcopy(cfg)
    extend_cfg(cfg)
    clean(cfg)
    mk_dir(cfg)
    mk_script(cfg)
    run_tool(cfg)










