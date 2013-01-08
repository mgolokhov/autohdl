import os
import shutil
import subprocess
import sys

from autohdl import hdlGlobals
from autohdl import toolchain
from autohdl import structure
from autohdl.hdlGlobals import synthesisPath, implementPath
import time

from autohdl.hdlLogger import log_call, logging
from autohdl import progressBar
from autohdl import git

log = logging.getLogger(__name__)


@log_call
def bit2mcs(config):
    try:
        if config['size']:
            proc = '{tool} -u 0 {top} -s {size} -w'.format(tool=toolchain.Tool().get('ise_promgen'),
                top=config['top'] + '.bit',
                size=config['size'])
            subprocess.check_call(proc)
        else:
            log.warning('PROM size was not set')
    except subprocess.CalledProcessError as e:
        log.error(e)
        sys.exit()


@log_call
def clean(path):
    try:
        if os.path.exists(path):
            for root, dirs, files in os.walk(path):
                for f in files:
                    if os.path.splitext(f)[1] not in ['.mcs', '.bit']:
                        os.remove(os.path.join(root, f))
    except OSError:
        log.warning("Can't clean folder " + path)
    if not os.path.exists(path):
        os.makedirs(path)


def copy_firmware(config):
    firmware_ext = ['.bit', '.mcs']
    dest_dir = os.path.join('..', 'resource')
    for i in os.listdir(dest_dir):
        if os.path.splitext(i)[1] in firmware_ext:
            print 'removing ', os.path.join(dest_dir, i)
            os.remove(os.path.join(dest_dir, i))

    for i in firmware_ext:
        src_abs_path = os.path.join(implementPath, config.get('top') + i)
        if os.path.exists(src_abs_path):
            # get latest version for this top git.get_last_build_num(top)
            dest = '{dsn}_{top}_build_{ver}{ext}'.format(
                dsn=os.path.basename(os.path.abspath('..')),
                top=config.get('top'),
                ver=git.get_last_build_num(config.get('top')) + 1,
                ext=i
            )
            dest_abs_path = os.path.join(dest_dir, dest)
            print 'copying', dest_abs_path
            shutil.copy(src_abs_path, dest_abs_path)


@log_call
def run(config):
    log.info("Implementation stage...")
    implPath = os.path.abspath(implementPath) + '/'
    synPath = os.path.abspath(synthesisPath) + '/'
    clean(implPath)
    top = os.path.join(synPath, config['top'] + '.edf')
    progressBar.run()
    cnt = 50
    while not os.path.exists(top) and cnt > 0:
        cnt -= 1
        time.sleep(1)
    progressBar.stop()
    if cnt == 0:
        log.error('Cant find netlist, try sythesis step first.')
        sys.exit(1)

    ucfSymplicity = structure.search(synPath, onlyExt='.ucf', ignoreDir=hdlGlobals.ignoreRepoDir)
    ucf = ucfSymplicity[0] or config['ucf']

    for i in config.get('depNetlist', []):
        shutil.copyfile(i, implPath + os.path.split(i)[1])
    shutil.copyfile(ucf, implPath + config['top'] + '.ucf')
    shutil.copyfile(top, implPath + config['top'] + '.edf')

    cwd_was = os.getcwd()
    os.chdir(implPath)
    while not os.path.exists(config['top'] + '.edf'):
        print 'cant find file: ', config['top']
        time.sleep(0.1)
    time.sleep(3)
    try:
        subprocess.check_call(('{xflow} -implement balanced.opt'
                               ' -config bitgen.opt {netlist}.edf').format(xflow=toolchain.Tool().get('ise_xflow'),
            netlist=config['top']))
        bit2mcs(config)
    except subprocess.CalledProcessError as e:
        log.error(e)
        sys.exit()
    finally:
        os.chdir(cwd_was)
    copy_firmware(config)
    log.info('Implementation done')

