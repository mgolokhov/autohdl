import os
import shutil
import subprocess
import time

from autohdl import toolchain, xilinx_env
from autohdl.hdlGlobals import synthesisPath

import logging
from autohdl.hdlLogger import log_call
import sys
from autohdl import progressBar

log = logging.getLogger(__name__)


@log_call
def getIncludePath(iPrj):
    incl = (iPrj.get('include_path', ".") or '.')
    return ';'.join(incl)


@log_call
def setParams(iPrj):
    synMacros = iPrj.get('SynMacros')# TODO: if you get None?
    print '-' * 10, synMacros
    if synMacros:
        synMacros = ' '.join(synMacros)
    else:
        synMacros = ""

    iPrj['scriptContent'] = iPrj['scriptContent'].format(
        #                          device=device,
        part=iPrj.get('part'),
        package=iPrj.get('package'),
        technology=iPrj.get('technology'),
        speed_grade=iPrj.get('speed_grade'),
        topModule=iPrj['top'],
        netlist=iPrj['top'] + '.edf',
        src_files=iPrj['srcFiles'],
        synMacros=synMacros,
        includePath=getIncludePath(iPrj))
    f = open(iPrj['pathScript'], 'w')
    f.write(iPrj['scriptContent'])
    f.close()


@log_call
def setSrc(iPrj):
    srcMain = iPrj.get('mainSrc')
    srcDep = iPrj.get('depSrc') or []
    ucf = iPrj.get('ucf')
    ucf = [ucf] if ucf else []
    #TODO: got duplicates, guess some bugs in structure
    srcFiles = set([i.replace('\\', '/') for i in srcMain + srcDep + ucf])
    iPrj['srcFiles'] = '\n'.join(['add_file "{0}"'.format(i) for i in srcFiles])


@log_call
def extend(prj):
    #TODO: convert all to abspath
    prj['pathTool'] = toolchain.Tool().get(prj['mode'])
    prj['pathSynthesis'] = synthesisPath
    prj['pathScript'] = prj['pathSynthesis'] + '/synthesis.prj'
    prj['pathLog'] = prj['top'] + '.srr'
    prj['pathWas'] = os.getcwd().replace('\\', '/')

    try:
        if os.path.exists(prj['pathSynthesis']):
            shutil.rmtree(prj['pathSynthesis'])
    except OSError as e:
        log.warning(e)

    for i in range(5):
        if os.path.exists(prj['pathSynthesis']):
            break
        else:
            time.sleep(0.5)
            try:
                os.makedirs(prj['pathSynthesis'])
            except OSError as e:
                log.warning(e)

    synthesis_template = os.path.join(os.path.dirname(__file__), 'data', 'template_synplify_prj')

    f = open(synthesis_template, 'r')
    prj['scriptContent'] = f.read()
    f.close()

    setSrc(prj)
    setParams(prj)

    return prj


@log_call
def parseLog(iPrj, iSilent=False):
    logFile = os.path.abspath(iPrj['pathLog'])
    if os.path.exists(logFile):
        f = open(logFile, 'r')
        res = f.read()
        log.info('See logfile: ' + logFile)
        log.info('Errors: {e}; Warnings: {w}'.format(
            e=res.count('@E:'),
            w=res.count('@W')
        ))

    return logFile


import threading

logging_synthesis_done = False

def logging_synthesis(iPrj):
    loge = ''
    for i in range(20):
        time.sleep(1)
        try:
            loge = open(iPrj['pathLog'], 'r')
            break
        except IOError as e:
            log.debug(e)

    if not loge:
        log.error('Cant start synthesis see ' + synthesisPath + '/stdout.log')
        sys.exit(1)

    while True:
        where = loge.tell()
        res = loge.readline()
        if res.endswith('\n'):
            print res
        elif logging_synthesis_done:
            break
        else:
            for dots in range(4):
                print '.' * dots,
                time.sleep(0.2)
                print '\r', ' ' * dots, '\r',
            loge.seek(where)

    loge.close()


@log_call
def run_synplify_batch(iPrj):
    run = '"%s" %s %s %s %s' % (iPrj['pathTool'],
                                '-product synplify_premier',
                                '-licensetype synplifypremier',
                                '-batch', 'synthesis.prj')
    p = threading.Thread(target=logging_synthesis, args=(iPrj,))
    p.setDaemon(1)
    p.start()
    global logging_synthesis_done
    try:
        subprocess.check_call(run, env=xilinx_env.get())
    except subprocess.CalledProcessError:
        print 'Synthesis error'
        logging_synthesis_done = True
        sys.exit(1)

    logging_synthesis_done = True


@log_call
def run_synplify_gui(iPrj):
    subprocess.check_call([iPrj['pathTool'], 'synthesis.prj'], env=xilinx_env.get())


@log_call
def runTool(iPrj, iSilent):
    """
    Runs external tool for synthesis
    """
    os.chdir(iPrj['pathSynthesis'])

    if iPrj['mode'] == 'synplify_batch':
        run_synplify_batch(iPrj=iPrj)
        parseLog(iPrj=iPrj, iSilent=iSilent)
    elif iPrj['mode'] == 'synplify_gui':
        run_synplify_gui(iPrj=iPrj)

    os.chdir(iPrj['pathWas'])


@log_call
def run(config):
    logging.info('Synthesis stage...')
    # changing current location to synthesis directory
    runTool(extend(config), iSilent=True)
    log.info('Synthesis done!')


