import os
import subprocess
import time
import logging
import sys

from autohdl import toolchain, xilinx_env
from autohdl.globals import synthesisPath
from autohdl import structure


alog = logging.getLogger(__name__)


#@log_call
def getIncludePath(config):
    incl = (config.get('include_path', ".") or '.')
    return ';'.join(incl)


#@log_call
def setParams(config):
    synMacros = config['hdlManager'].get('SynMacros')
    if synMacros and synMacros != 'None':
        synMacros = ' '.join(synMacros)
    else:
        synMacros = ""

    config['synplify']['scriptContent'] = config['synplify']['scriptContent'].format(
        part=config['hdlManager'].get('part'),
        package=config['hdlManager'].get('package'),
        technology=config['hdlManager'].get('technology'),
        speed_grade=config['hdlManager'].get('speed_grade'),
        topModule=config['hdlManager']['top'],
        netlist=config['hdlManager']['top'] + '.edf',
        src_files=config['synplify']['srcFiles'],
        synMacros=synMacros,
        includePath=getIncludePath(config))
    f = open(config['synplify']['pathScript'], 'w')
    f.write(config['synplify']['scriptContent'])
    f.close()


def setSrc(config):
    srcMain = config['structure']['mainSrc']
    srcDep = config['structure'].get('depSrc') or []
    sdc = config['hdlManager'].get('sdc')
    ucf = [config['hdlManager'].get('ucf')] or []
    if not sdc:
        alog.warning('Set sdc constraint file before synthesis')
        sdc = []
    else:
        sdc = [sdc]
    #TODO: got duplicates, guess some bugs in structure
    # srcFiles = set([i.replace('\\', '/') for i in srcMain + srcDep + sdc + ucf])
    srcFiles = [i.replace('\\', '/') for i in srcMain + srcDep + sdc + ucf]
    config['synplify']['srcFiles'] = '\n'.join(['add_file "{0}"'.format(i) for i in srcFiles])


#@log_call
def extend(config):
    #TODO: convert all to abspath
    config['synplify']['pathTool'] = toolchain.Tool().get('synplify_' +
                                                          config['hdlManager']['cl']['synplify'])
    config['synplify']['pathSynthesis'] = synthesisPath + '/' + config['hdlManager']['top']
    config['synplify']['pathScript'] = config['synplify']['pathSynthesis'] + '/synthesis.prj'
    config['synplify']['pathLog'] = config['hdlManager']['top'] + '.srr'
    config['synplify']['pathWas'] = os.getcwd().replace('\\', '/')

    for i in range(5):
        if os.path.exists(config['synplify']['pathSynthesis']):
            break
        else:
            time.sleep(0.5)
            try:
                os.makedirs(config['synplify']['pathSynthesis'])
            except OSError as e:
                alog.warning(e)

    synthesis_template = os.path.join(os.path.dirname(__file__), 'data', 'template_synplify_prj')

    f = open(synthesis_template, 'r')
    config['synplify']['scriptContent'] = f.read()
    f.close()

    setSrc(config)
    setParams(config)

    return config


#@log_call
def parseLog(config):
    log_file = os.path.abspath(config['synplify']['pathLog'])
    errors = True  # no log file
    if os.path.exists(log_file):
        f = open(log_file, 'r')
        res = f.read()
        alog.info('See logfile: ' + log_file)
        errors = res.count('@E:')
        alog.info('Errors: {e}; Warnings: {w}'.format(
            e=errors,
            w=res.count('@W')
        ))
    alog.info(log_file)
    if errors:
        sys.exit(1)
    return log_file


import threading

logging_synthesis_done = False


def logging_synthesis(config):
    loge = ''
    for i in range(20):
        time.sleep(1)
        try:
            loge = open(config['synplify']['pathLog'], 'r')
            break
        except IOError as e:
            alog.debug(e)

    if not loge:
        alog.error('Cant start synthesis see ' + synthesisPath + '/stdout.log')
        sys.exit(1)

    while True:
        where = loge.tell()
        res = loge.readline()
        if res.endswith('\n'):
            print(res)
        elif logging_synthesis_done:
            break
        else:
            print('.', end=' ')
            time.sleep(1)
            sys.stdout.flush()
            loge.seek(where)
    loge.close()


#@log_call
def run_synplify_batch(config):
    run = '"%s" %s %s %s %s' % (config['synplify']['pathTool'],
                                '-product synplify_premier',
                                '-licensetype synplifypremier',
                                '-batch', 'synthesis.prj')
    if config['hdlManager'].get('debug') == 'hardcore_test':
        config.setdefault('execution_fifo', [])
        config['execution_fifo'].append(run)
        return
    p = threading.Thread(target=logging_synthesis, args=(config,))
    p.setDaemon(1)
    p.start()
    global logging_synthesis_done
    try:
        #TODO: handle err
        # 0 - OK
        # 2 - logical error
        # 3 - startup failure
        # 4 - licensing failure
        # 5 - batch not available
        # 6 - duplicate-user error
        # 7 - project-load error
        # 8 - command-line error
        # 9 - Tcl-script error
        # 20 - graphic-resource error
        # 21 - Tcl-initialization error
        # 22 - job-configuration error
        # 23 - parts error
        # 24 - product-configuration error
        # 25 - multiple top levels
        subprocess.check_call(run, env=xilinx_env.get())
    except subprocess.CalledProcessError as e:
        alog.error('Synthesis error '+str(e))
        logging_synthesis_done = True
        sys.exit(1)

    logging_synthesis_done = True


#@log_call
def run_synplify_gui(config):
    run = config['synplify']['pathTool'] + ' synthesis.prj'
    if config['hdlManager'].get('debug') == 'hardcore_test':
        config.setdefault('execuiton_fifo', [])
        config['execution_fifo'].append(run)
        return
    subprocess.check_call(run, env=xilinx_env.get())


#@log_call
def runTool(config):
    """
    Runs external tool for synthesis
    """
    os.chdir(config['synplify']['pathSynthesis'])

    if config['hdlManager']['cl']['synplify'] == 'batch':
        run_synplify_batch(config=config)
        sys.stdout.flush()
        parseLog(config=config)
    elif config['hdlManager']['cl']['synplify'] == 'gui':
        run_synplify_gui(config=config)

    os.chdir(config['synplify']['pathWas'])


#@log_call
def run(config):
    config['synplify'] = dict()
    logging.info('Synthesis stage...')
    # changing current location to synthesis directory
    runTool(extend(config))
    alog.info('Synthesis done!')


