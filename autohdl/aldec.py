import os
import shutil
import subprocess

from autohdl.hdlLogger import log_call
from autohdl import structure
from autohdl import build
from autohdl import hdlGlobals
from autohdl import template_avhdl_adf
from autohdl import toolchain
from autohdl.hdlGlobals import aldecPath


@log_call
def extend(config):
    """
    Precondition: cwd= <dsn_name>/script
    Output: dictionary { keys=main, dep, tb, other values=list of path files}
    """
    config.setdefault('aldec', dict())
    config['aldec']['rootPath'] = os.path.abspath('..').replace('\\', '/')
    config['aldec']['dsnName'] = os.path.basename(config['aldec']['rootPath'])

    config['aldec']['allSrc'] = structure.search(directory=config['aldec']['rootPath'],
                                                 ignoreDir=hdlGlobals.ignoreRepoDir + ['autohdl'])

    config['aldec']['srcUncopied'] = structure.search(directory=aldecPath + '/src',
                                                      onlyExt=hdlGlobals.hdlFileExt,
                                                      ignoreDir=hdlGlobals.ignoreRepoDir)

    config['aldec']['TestBenchSrc'] = structure.search(directory='../TestBench', ignoreDir=hdlGlobals.ignoreRepoDir)

    config['aldec']['netlistSrc'] = structure.search(directory=aldecPath + '/src',
                                                     onlyExt='.sedif .edn .edf .edif .ngc'.split())

    config['aldec']['filesToCompile'] = (config['aldec']['allSrc'] + config['structure']['depSrc'])

    #add cores designs (ignore repo files) to project navigator
    if os.path.basename(os.path.abspath('../..')) == 'cores':
        # repo/cores/dsn/script/
        config['aldec']['repoPath'] = os.path.abspath('../../..').replace('\\', '/')
    elif 'cores' in os.listdir('../..'):
        # repo/dsn/script
        config['aldec']['repoPath'] = os.path.abspath('../..').replace('\\', '/')
    else:
        config['aldec']['repoPath'] = None
    config['aldec']['repoSrc'] = []
    if config['aldec']['repoPath']:
        for root, dirs, files in os.walk(config['aldec']['repoPath']):
            if config['aldec']['dsnName'] in dirs:
                dirs.remove(config['aldec']['dsnName'])
            for i in ['aldec', 'synthesis', 'implement', '.svn', '.git', 'TestBench', 'script', 'resource']:
                if i in dirs:
                    dirs.remove(i)
            for f in files:
                if 'src' in root + '/' + f:
                    config['aldec']['repoSrc'].append(os.path.abspath(root + '/' + f).replace('\\', '/'))
    config['build'] = build.load()


@log_call
def gen_aws(iPrj):
    content = '[Designs]\n{dsn}=./{dsn}.adf'.format(dsn=iPrj['aldec']['dsnName'])
    with open(aldecPath + '/wsp.aws', 'w') as f:
        f.write(content)


@log_call
def gen_adf(iPrj):
    adf = template_avhdl_adf.generate(iPrj=iPrj)
    with open(aldecPath + '/{dsn}.adf'.format(dsn=iPrj['aldec']['dsnName']), 'w') as f:
        f.write(adf)


@log_call
def gen_compile_cfg(config):
    src = []
    for i in config['aldec']['filesToCompile']:
        if os.path.splitext(i)[1] not in hdlGlobals.hdlFileExt:
            continue
        path = os.path.abspath(i)
        try:
            res = '[file:.\\{0}]\nEnabled=1'.format(os.path.relpath(path=path, start=aldecPath))
        except ValueError:
            print 'FUCKUP ' * 10
            res = '[file:{0}]\nEnabled=1'.format(i)
        src.append(res)
    with open(aldecPath + '/compile.cfg', 'w') as f:
        f.write('\n'.join(src))


@log_call
def cleanAldec():
    if not {'resource', 'script', 'src', 'TestBench'}.issubset(os.listdir(os.getcwd() + '/..')):
        return
    cl = structure.search(directory=aldecPath, ignoreDir=['implement', 'synthesis', 'src'])
    for i in cl:
        if os.path.isdir(i):
            shutil.rmtree(i)
        else:
            os.remove(i)


@log_call
def copyNetlists():
    netLists = structure.search(directory='../src',
                                onlyExt='.sedif .edn .edf .edif .ngc'.split(),
                                ignoreDir=['.git', '.svn', 'aldec'])
    for i in netLists:
        shutil.copyfile(i, aldecPath + '/src/' + os.path.split(i)[1])


@log_call
def genPredefined():
    predef = hdlGlobals.predefDirs + ['dep']
    for i in predef:
        folder = aldecPath + '/src/' + i
        if not os.path.exists(folder):
            os.makedirs(folder)


@log_call
def preparation():
    cleanAldec()
    genPredefined()
    copyNetlists()


@log_call
def export(config):
    preparation()
    extend(config)
    gen_aws(config)
    gen_adf(config)
    gen_compile_cfg(config)
    aldec = toolchain.Tool().get('avhdl_gui')
    config.setdefault('execution_fifo', list())
    config['execution_fifo'].append('python{mode} {abs_path_to}/aldec_run.py {current_dir} "{aldec_exe}"'.format(
        abs_path_to=os.path.dirname(__file__),
        current_dir=os.getcwd(),
        aldec_exe=aldec,
        mode='' if config['hdlManager'].get('debug') else 'w'
    ))
    if config['hdlManager'].get('debug') != 'hardcore_test':
        for i in config['execution_fifo']:
            subprocess.Popen(i)
