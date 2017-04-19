import os
import shutil
import subprocess

from autohdl import structure
# from autohdl import build
# from autohdl import hdlGlobals
from autohdl import template_avhdl_adf
from autohdl import toolchain
from autohdl import ALDEC_PATH, PREDEFINED_DIRS, IGNORE_REPO_DIRS, VERILOG_VHDL_FILE_EXT


def extend(config):
    """
    Precondition: cwd= <dsn_name>/script
    Output: dictionary { keys=main, dep, tb, other values=list of path files}
    """
    config.setdefault('aldec', dict())
    config['aldec']['rootPath'] = os.path.abspath('..').replace('\\', '/')
    config['aldec']['dsnName'] = os.path.basename(config['aldec']['rootPath'])

    config['aldec']['allSrc'] = structure.search(directory=config['aldec']['rootPath'],
                                                 ignoreDir=IGNORE_REPO_DIRS + ('autohdl',))

    config['aldec']['srcUncopied'] = structure.search(directory=ALDEC_PATH + '/src',
                                                      onlyExt=VERILOG_VHDL_FILE_EXT,
                                                      ignoreDir=IGNORE_REPO_DIRS)

    config['aldec']['TestBenchSrc'] = structure.search(directory='../TestBench', ignoreDir=IGNORE_REPO_DIRS)
    config['aldec']['TestBenchUtils'] = structure.search(directory='../../TestBenchUtils', ignoreDir=IGNORE_REPO_DIRS)
    if config['aldec']['TestBenchUtils']:
        config['aldec']['TestBenchSrc'] += config['aldec']['TestBenchUtils']

    config['aldec']['netlistSrc'] = structure.search(directory=ALDEC_PATH + '/src',
                                                     onlyExt='.sedif .edn .edf .edif .ngc'.split())

    config['aldec']['filesToCompile'] = (config['aldec']['allSrc']
                                         #+ config['structure']['depSrc']
                                         + config['aldec']['TestBenchSrc'])

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
    #config['build'] = build.load()


def gen_aws(iPrj):
    content = '[Designs]\n{dsn}=./{dsn}.adf'.format(dsn=iPrj['aldec']['dsnName'])
    with open(ALDEC_PATH + '/wsp.aws', 'w') as f:
        f.write(content)


def gen_adf(iPrj):
    adf = template_avhdl_adf.generate(iPrj=iPrj)
    with open(ALDEC_PATH + '/{dsn}.adf'.format(dsn=iPrj['aldec']['dsnName']), 'w') as f:
        f.write(adf)


def gen_compile_cfg(config):
    src = []
    for i in config['aldec']['filesToCompile']:
        if os.path.splitext(i)[1] not in VERILOG_VHDL_FILE_EXT:
            continue
        path = os.path.abspath(i)
        try:
            res = '[file:.\\{0}]\nEnabled=1'.format(os.path.relpath(path=path, start=ALDEC_PATH))
        except ValueError:
            print('FUCKUP ' * 10)
            res = '[file:{0}]\nEnabled=1'.format(i)
        src.append(res)
    with open(ALDEC_PATH + '/compile.cfg', 'w') as f:
        f.write('\n'.join(src))


def cleanAldec():
    if not {'resource', 'script', 'src', 'TestBench'}.issubset(os.listdir(os.getcwd() + '/..')):
        return
    cl = structure.search(directory=ALDEC_PATH, ignoreDir=['implement', 'synthesis', 'src'])
    for i in cl:
        if os.path.isdir(i):
            shutil.rmtree(i)
        else:
            os.remove(i)


def copyNetlists():
    netLists = structure.search(directory='../src',
                                onlyExt='.sedif .edn .edf .edif .ngc'.split(),
                                ignoreDir=['.git', '.svn', 'aldec'])
    for i in netLists:
        shutil.copyfile(i, ALDEC_PATH + '/src/' + os.path.split(i)[1])


def genPredefined():
    predef = PREDEFINED_DIRS + ('dep',)
    for i in predef:
        folder = ALDEC_PATH + '/src/' + i
        if not os.path.exists(folder):
            os.makedirs(folder)


def preparation():
    # cleanAldec()
    genPredefined()
    # copyNetlists()


def export(config):

    import pprint
    pprint.pprint(config)

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
        mode='w' #if config['hdlManager'].get('debug') else 'w'
    ))
    doit = 'python{mode} {abs_path_to}/aldec_run.py {current_dir} "{aldec_exe}"'.format(
        abs_path_to=os.path.dirname(__file__),
        current_dir=os.getcwd(),
        aldec_exe=aldec,
        mode='w' #if config['hdlManager'].get('debug') else 'w'
    )
    subprocess.Popen(doit)
    # if config['hdlManager'].get('debug') != 'hardcore_test':
    #     for i in config['execution_fifo']:
    #         subprocess.Popen(i)
