import os
import subprocess
import time
import logging
import sys
import threading
import copy
import pprint

from autohdl import toolchain, xilinx
from autohdl import SYNTHESIS_PATH

alog = logging.getLogger(__name__)


PRJ_TEMPLATE = """\
#Source files
{src_files}

#device options
set_option -technology {technology}
set_option -part {part}
set_option -package {package}
set_option -speed_grade {speed_grade}

set_option -vlog_std sysv

#compilation/mapping options
set_option -hdl_define -set {synMacros}

#map options
set_option -top_module "{topModule}"
set_option -include_path "{includePath}"

#simulation options
project -result_format "edif"
project -result_file "{netlist}"
"""

ERR_CODES = {
    0: 'OK',
    2: 'logical error',
    3: 'startup failure',
    4: 'licensing failure',
    5: 'batch not available',
    6: 'duplicate-user error',
    7: 'project-load error',
    8: 'command-line error',
    9: 'Tcl-script error',
    20: 'graphic-resource error',
    21: 'Tcl-initialization error',
    22: 'job-cfguration error',
    23: 'parts error',
    24: 'product-cfguration error',
    25: 'multiple top levels',
}

def form_prj_files(cfg):
    # src and constraints
    prj_files = [i.replace('\\', '/') for i in cfg['src']]
    return '\n'.join(['add_file "{0}"'.format(i) for i in prj_files])


def form_include_paths(cfg):
    incl = (cfg.get('include_paths', ".") or '.')
    return ';'.join(incl)


def form_macros(cfg):
    # defines
    synMacros = cfg.get('SynMacros')
    if synMacros and synMacros != 'None':
        synMacros = ' '.join(synMacros)
    else:
        synMacros = ""
    return synMacros


def mk_script(cfg):
    project_script_content = PRJ_TEMPLATE.format(
        part=cfg.get('part'),
        package=cfg.get('package'),
        technology=cfg.get('technology'),
        speed_grade=cfg.get('speed_grade'),
        topModule=cfg['top_module'],
        netlist=cfg['top_module'] + '.edf',
        src_files=form_prj_files(cfg),
        synMacros=form_macros(cfg),
        includePath=form_include_paths(cfg))

    with open(cfg['prj_script'], 'w') as f:
        f.write(project_script_content)


def extend_cfg(cfg):
    cfg['tool'] = toolchain.Tool().get('synplify_' + cfg['synplify'])
    cfg['prj_dir'] = os.path.abspath(os.path.join(SYNTHESIS_PATH, cfg['top_module']))
    cfg['prj_script'] = os.path.abspath(os.path.join(cfg['prj_dir'], 'synthesis.prj'))
    cfg['result'] = os.path.abspath(os.path.join(cfg['prj_dir'], cfg['top_module'] + '.srr'))
    cfg['cwd_was'] = os.getcwd()
    return cfg


def parse_log(cfg):
    log_file = os.path.abspath(cfg['result'])
    errors = True  # no log file
    if os.path.exists(log_file):
        f = open(log_file)
        res = f.read()
        alog.info('See logfile: ' + log_file)
        errors = res.count('@E:')
        alog.info('Errors: {e}; Warnings: {w}'.format(
            e=errors,
            w=res.count('@W')
        ))
    if errors:
        sys.exit(1)
    return log_file


def logging_synthesis(cfg):
    loge = None
    for i in range(20):
        try:
            loge = open(cfg['result'])
            break
        except IOError as e:
            alog.debug(e)
        time.sleep(1)

    if not loge:
        with open(os.path.join(SYNTHESIS_PATH, cfg['top_module'], 'stdout.log')) as f:
            print(f.read())
        sys.exit(1)

    while True:
        where = loge.tell()
        res = loge.readline()
        if res.endswith('\n'):
            print(res)
        elif cfg['logging_synthesis_done']:
            print('.', end=' ')
            time.sleep(1)
            sys.stdout.flush()
            loge.seek(where)
            loge.close()
            return
        else:
            print('.', end=' ')
            time.sleep(1)
            sys.stdout.flush()
            loge.seek(where)



def run_synplify_batch(cfg):
    cl_run = "{} -product synplify_premier -licensetype synplifypremier -batch {}".format(cfg['tool'],
                                                                                          cfg['prj_script'])
    try:
        if os.path.exists(cfg['result']):
            os.remove(cfg['result'])
    except Exception as e:
        alog.error(e)
    cfg['logging_synthesis_done'] = False
    p = threading.Thread(target=logging_synthesis, args=(cfg,), daemon=True)
    p.start()
    try:
        subprocess.check_call(cl_run, env=xilinx.load_env_settings())

    except subprocess.CalledProcessError as e:
        alog.error('Synthesis: {} (exit code {})'.format(ERR_CODES[e.returncode], e.returncode))
        sys.exit(1)
    finally:
        cfg['logging_synthesis_done'] = True
        alog.info('Synthesis done')


def run_tool(cfg):
    os.chdir(cfg['prj_dir'])

    if cfg['synplify'] == 'batch':
        run_synplify_batch(cfg=cfg)
        sys.stdout.flush()
        parse_log(cfg=cfg)
    elif cfg['synplify'] == 'gui':
        subprocess.check_call(cfg['tool'] + ' ' + cfg['prj_script'],
                              env=xilinx.load_env_settings())

    os.chdir(cfg['cwd_was'])


def mk_dir(cfg):
    for i in range(5):
        if os.path.exists(cfg['prj_dir']):
            return
        else:
            time.sleep(0.5)
            try:
                os.makedirs(cfg['prj_dir'])
            except OSError as e:
                alog.warning(e)  
                

def run(cfg):
    # create project dir
    # generate project script (src, params)
    # execute tool and parse log
    alog.info('Synthesis stage...')
    cfg = copy.deepcopy(cfg)
    extend_cfg(cfg)
    mk_dir(cfg)
    mk_script(cfg)
    alog.debug(pprint.pformat(cfg))
    run_tool(cfg)
    return cfg




