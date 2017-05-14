import os
import shutil
import subprocess
import pprint

from autohdl import structure
from autohdl import template_avhdl_adf
from autohdl import toolchain
from autohdl import ALDEC_PATH, PREDEFINED_DIRS, IGNORE_REPO_DIRS, VERILOG_VHDL_FILE_EXT


def extend(config):
    """
    Precondition: cwd= <dsn_name>/script
    Output: dictionary { keys=main, dep, tb, other values=list of path files}
    """
    # netlists should be copied in the real folders for synthesis and implementation
    config.setdefault('aldec', dict())
    config['aldec']['dsn_root'] = os.path.normpath(config.get('dsn_root'))
    config['aldec']['wsp_root'] = os.path.normpath(os.path.join(config.get('dsn_root'), '..'))
    config['aldec']['src'] = [os.path.normpath(i) for i in config['src']]
    config['aldec']['dsn_name'] = config.get('dsn_name')
    config['aldec']['all_src'] = structure.search(directory=config['aldec']['wsp_root'],
                                                  ignore_dir=IGNORE_REPO_DIRS + ('autohdl',),
                                                  ignore_ext=('.DS_Store',)
                                                  )
    config['aldec']['dsn_src'] = structure.search(directory=config['aldec']['dsn_root'],
                                                  ignore_dir=IGNORE_REPO_DIRS + ('autohdl',),
                                                  ignore_ext=('.DS_Store',)
                                                  )
    #pprint.pprint(config['aldec']['dsn_src'])
    #import sys; sys.exit(0);
    config['aldec']['deps'] = [i for i in config['aldec']['src'] if config['aldec']['dsn_root'] not in i]


def gen_aws(config):
    content = '[Designs]\n{dsn}=./{dsn}.adf'.format(dsn=config['aldec']['dsn_name'])
    with open(ALDEC_PATH + '/wsp.aws', 'w') as f:
        f.write(content)


def gen_adf(config):
    adf = template_avhdl_adf.generate(iPrj=config)
    with open(ALDEC_PATH + '/{dsn}.adf'.format(dsn=config['aldec']['dsn_name']), 'w') as f:
        f.write(adf)


def gen_compile_cfg(config):
    src = []
    for i in config['aldec']['dsn_src'] + config['aldec']['deps']:
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


def clean_aldec():
    if not {'resource', 'script', 'src', 'TestBench'}.issubset(os.listdir(os.getcwd() + '/..')):
        return
    cl = structure.search(directory=ALDEC_PATH, ignore_dir=['implement', 'synthesis', 'src'])
    for i in cl:
        try:
            if os.path.isdir(i):
                shutil.rmtree(i)
            else:
                os.remove(i)
        except Exception as e:
            pass


def copy_netlists():
    netLists = structure.search(directory='../src',
                                only_ext='.sedif .edn .edf .edif .ngc'.split(),
                                ignore_dir=['.git', '.svn', 'aldec'])
    for i in netLists:
        shutil.copyfile(i, ALDEC_PATH + '/src/' + os.path.split(i)[1])


def genPredefined():
    predef = PREDEFINED_DIRS + ('dep',)
    for i in predef:
        folder = ALDEC_PATH + '/src/' + i
        if not os.path.exists(folder):
            os.makedirs(folder)


def preparation():
    #clean_aldec()
    genPredefined()
    # copyNetlists()


def export(config):
    preparation()
    extend(config)
    gen_aws(config)
    gen_adf(config)
    gen_compile_cfg(config)
    aldec = toolchain.Tool().get('avhdl_gui')
    config.setdefault('execution_fifo', list())
    doit = 'python{mode} {abs_path_to}/aldec_run.py {current_dir} "{aldec_exe}"'.format(
        abs_path_to=os.path.dirname(__file__),
        current_dir=os.getcwd(),
        aldec_exe=aldec,
        mode='w'
    )
    # pprint.pprint(config)
    subprocess.Popen(doit)

