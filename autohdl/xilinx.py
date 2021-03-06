import os
import shutil
import subprocess
import sys
import time
from time import strftime
import locale
import copy
import logging
import autohdl.utils as utils
import re

from autohdl import toolchain
from autohdl import IMPLEMENT_PATH, SYNTHESIS_PATH, NETLIST_EXT


alog = logging.getLogger(__name__)


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
    eeprom_kilobytes = cfg.get('eeprom_kilobytes') or cfg.get("mcs")
    try:
        if eeprom_kilobytes:
            proc = '{tool} -u 0 {top} -s {size} -w'.format(tool=toolchain.Tool().get('ise_promgen'),
                                                           top=cfg['bit_file'],
                                                           size=eeprom_kilobytes)
            print(proc)
            subprocess.check_call(proc)
        else:
            alog.warning('EEPROM size was not set')
    except subprocess.CalledProcessError as e:
        alog.error(e)
        sys.exit(1)


def copy_firmware(cfg):
    # get old firmwares by ext
    # get new firmwares by ext
    # compare and copy if new contents (sha), append current timestamp
    firmware_ext = ('.bit', '.mcs',)
    build_timestamp = strftime('%y%m%d_%H%M%S', time.localtime())
    dest_dir = os.path.join(cfg['dsn_root'], 'resource')
    search_dir = os.path.join(cfg['dsn_root'], 'autohdl', 'implement', cfg['top_module'])
    fw_old = [i for i in os.listdir(dest_dir) if os.path.splitext(i)[1] in firmware_ext and cfg['dsn_name']+'_'+cfg['top_module'] in i]
    for ext in firmware_ext:
        src_path = os.path.join(search_dir, cfg['top_module'] + ext)
        if os.path.exists(src_path):
            dst_path = "{path}/{dsn}_{top}_{time}{ext}".format(path=dest_dir,
                                                               dsn=cfg['dsn_name'],
                                                               top=cfg['top_module'],
                                                               time=build_timestamp,
                                                               ext=ext)
            dst_path_old = None
            for fname_old in fw_old:
                pattern = "{dsn}_{top}_{date}{ext}".format(dsn=cfg['dsn_name'],
                                                           top=cfg['top_module'],
                                                           date='\d{6}_\d{6}',
                                                           ext=ext)
                if re.search(pattern=pattern, string=fname_old):
                    dst_path_old = os.path.join(dest_dir, fname_old)
                    if not utils.is_same_contents(src_path, dst_path_old):
                        alog.info("Remove old firmware: "+dst_path_old)
                        try:
                            os.remove(dst_path_old)
                        except IOError:
                            pass  # intentional
                        alog.info('Copy new firmware: '+dst_path)
                        shutil.copy(src_path, dst_path)
                    else:
                        alog.info("No need to replace, same contents: "+dst_path_old)
            if not dst_path_old:
                alog.info('Copy new firmware '+dst_path)
                shutil.copy(src_path, dst_path)



def clean(cfg):
    for i in range(3):
        if os.path.exists(cfg['prj_dir']):
            try:
                shutil.rmtree(cfg['prj_dir'])
                break
            except Exception as e:
                alog.warning(e)
                time.sleep(1)
    if os.path.exists(cfg['prj_dir']):
        message = "Can't clean xilinx project {}".format(cfg['prj_dir'])
        alog.error(message)
        sys.exit(message)


def mk_dir(cfg):
    for i in range(3):
        if not os.path.exists(cfg['prj_dir']):
            try:
                os.makedirs(cfg['prj_dir'])
                break
            except Exception as e:
                alog.warning(e)
                time.sleep(1)
    if not os.path.exists(cfg['prj_dir']):
        message = "Can't make xilinx project {}".format(cfg['prj_dir'])
        alog.error(message)
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
        encoding = locale.getdefaultlocale()[1]
        res = subprocess.check_output('cmd /c "call {0} & set"'.format(wrapper.replace('/', '\\')))
        res = res.decode(encoding)
        d = {}
        #create key=value environment variables
        for i in res.split(os.linesep):
            res = i.split('=')
            if len(res) == 2:
                d.update({res[0]: res[1]})
        alog.info("Load xilinx env from: "+wrapper)
        return d
    except Exception as exp:
        alog.error(exp)


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










