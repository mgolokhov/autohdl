import argparse
import glob
import logging
import os
import pprint
import sys
import cgitb
cgitb.enable(format='text')

from autohdl import structure
from autohdl import build
from autohdl import synplify
from autohdl import aldec
from autohdl import xilinx

from autohdl import publisher

alog = logging.getLogger(__name__)

#@log_call
def validateTop(iTop, config):
    parsed = config.setdefault('structure', dict()).get('parsed')
    if not parsed:
        structure.setSrc(config)
        parsed = config['structure']['parsed']

    if iTop and parsed.get(iTop):
        return True


#@log_call
def getFullPathToUcf(iUcf):
    # could be
    # empty
    # valid full path
    # wrong name\path
    # just name without extension
    # name with extension
    if not iUcf:
        return False
    if os.path.exists(iUcf):
        return os.path.abspath(iUcf).replace('\\', '/')
    # <filename>.ucf or just <filename>
    path = os.path.abspath('../src/{}.ucf'.format(os.path.splitext(iUcf)[0])).replace('\\', '/')
    if os.path.exists(path):
        return path


#@log_call
def setValidTop(arguments, config):
    try:
        topAsScriptName = os.path.splitext(os.path.basename(sys.modules['__main__'].__file__))[0]
    except AttributeError as e:
        alog.debug(e)
        topAsScriptName = ''

    if validateTop(arguments.top, config):
        config['hdlManager']['top'] = arguments.top
        alog.info('Using top module name from arguments list')
    elif topAsScriptName and validateTop(topAsScriptName, config):
        config['hdlManager']['top'] = topAsScriptName
        alog.info('Using top module name same as script name')
    elif validateTop(config['hdlManager'].get('top'), config):
        alog.info('Using top module name from merged configs (build.yaml and script)')
    else:
        top = build.load().get('top')
        if validateTop(top, config):
            alog.info('Using top module from build.yaml')
            config['hdlManager']['top'] = top
        else:
            config['hdlManager']['top'] = ''
            alog.error('Top module name undefined!')


#@log_call
def setValidUcf(config):
    top = config['hdlManager'].get('top')
    if top:
        ucfNameAsTop = getFullPathToUcf(top)
        if ucfNameAsTop:
            config['hdlManager']['ucf'] = ucfNameAsTop
            alog.info('Using ucf name same as top module')
            return

    ucfFromScript = getFullPathToUcf(config['hdlManager']['ucf'])
    if ucfFromScript:
        config['hdlManager']['ucf'] = ucfFromScript
        alog.info('Using ucf file from script')
        return

    ucfFromBuild = getFullPathToUcf(build.load().get('ucf'))
    if ucfFromBuild:
        config['hdlManager']['ucf'] = ucfFromBuild
        alog.info('Using ucf file from build.yaml')
        return

    # if only one ucf file
    res = glob.glob('../src/*.ucf')
    if len(res) == 1:
        config['hdlManager']['ucf'] = getFullPathToUcf(res[0])
        alog.info('Found only one ucf file, using it')
        return
    elif len(res) == 0:
        alog.info('Cant find ucf file')
    else:
        alog.info('Found many ucf files, cant define which one to use')

    alog.warning('Ucf file undefined')


#@log_call
def validateLocation():
    # for Active-hdl compatibility, possibility to run in project navigator
    try:
        if not {'script', 'src'}.issubset(os.listdir(os.getcwd() + '/..')):
            mayBe = os.path.dirname(sys.modules['__main__'].__file__)
            if {'script', 'src'}.issubset(os.listdir(mayBe + '/..')):
                os.chdir(mayBe)
            else:
                alog.error('Wrong current working path!\n Tried: \n{}\n{}'.format(
                    os.getcwd(),
                    mayBe
                ))
                sys.exit()
    except AttributeError as e:
        alog.debug(e)
    except WindowsError as e:
        alog.debug(e)


#@log_call
def mergeConfig(configScript, configBuild):
    """
    Rewrites all params in configBuild by configScript, except 'dep' (it's extended);
    """
    depInScript = configScript.pop('dep', []) or []
    configBuild.update(configScript)
    if depInScript:
        configBuild['dep'] = depInScript + (configBuild.get('dep', []) or [])
    return configBuild


#@log_call
def printInfo(config):
    alog.info(('Main design settings:\n'
               + '#' * 40 +
               '\n'
               'technology : {technology}\n'
               'part       : {part}\n'
               'package    : {package}\n'
               'top module : {top}\n'
               'ucf        : {ucf}\n'
               'PROM size  : {size} kilobytes\n'
               + '#' * 40 +
               '').format(technology=config['hdlManager'].get('technology'),
                          part=config['hdlManager'].get('part'),
                          package=config['hdlManager'].get('package'),
                          top=config['hdlManager'].get('top'),
                          ucf=config['hdlManager'].get('ucf'),
                          size=config['hdlManager'].get('size'),
                          upload=config['hdlManager'].get('upload')))


# priority in searching top module name:
#   1 name set by command line (-top <top_name>)
#   2 name of python script (top_name.py)
#   3 name set in python script (top="<top_name>")
#   4 name in build.yaml (top:<top_name>)
# priority in searching ucf file:
#   1 same name as top module
#   2 name in python script <ucf_filename>[.ucf]
#   3 path in build.yaml (absolute or relative path)
#   4 any single ucf file in "src" folder
#@log_call
def kungfu(**configScript):
    alog.info('Processing...')
    alog.debug('args: ' + str(sys.argv))
    alog.debug('config: ' + str(configScript))

    validateLocation()
    configBuild = build.load(cacheEnable=False)
    build.compare_global(configScript)
    build.compare_global(configBuild)
    build.dump(configBuild)
    config = dict()
    config['hdlManager'] = mergeConfig(configScript, configBuild)

    parser = argparse.ArgumentParser(description='HDL Manager')
    parser.add_argument('-tb', nargs='?', const='aldec',
                        choices=['aldec', 'verilator_not_yet'],
                        help='export project to active-hdl [default=aldec]')
    parser.add_argument('-top', help='set/redefine top module name [has highest priority]')
    parser.add_argument('-synplify', nargs='?', const='batch',
                        choices=['batch', 'gui'],
                        help='synthesis step [default=batch]')
    parser.add_argument('-xilinx', nargs='?', const='batch',
                        choices=['batch', 'gui', 'gui-clean'],
                        help='implementation step [default=batch]')
    parser.add_argument('-mcs', nargs='?', const='config', help='generate .mcs from .bit file')
    parser.add_argument('-upload', action='store_true', help='upload firmware to WebDav server')
    parser.add_argument('-message', help='information about firmware')
    parser.add_argument('-debug', nargs='?', const='normal',
                        choices=['normal', 'hardcore_test'],
                        help='debug mode')
    arguments = parser.parse_args()

    setValidTop(arguments, config)
    setValidUcf(config)
    config['hdlManager']['dsn_root'] = os.path.dirname(os.getcwd())
    config['hdlManager']['dsn_name'] = os.path.basename(config['hdlManager']['dsn_root'])

    if arguments.mcs and arguments.mcs != 'config':
        # redefine default value from configure files (kungfu.py, build.yaml)
        config['hdlManager']['size'] = arguments.mcs

    config['hdlManager']['cl'] = vars(arguments)

    if arguments.debug == 'normal':
        alog.info('\n' + pprint.pformat(config))
        return config

    printInfo(config)

    if len(sys.argv) == 1:
        config['hdlManager']['cl']['synplify'] = 'batch'
        synplify.run(config)
        config['hdlManager']['cl']['xilinx'] = 'batch'
        xilinx.run_project(config)
        xilinx.bit2mcs(config)
        xilinx.copy_firmware(config)
        return

    if arguments.tb:
        aldec.export(config)
    if arguments.synplify:
        synplify.run(config)
    if arguments.xilinx:
        xilinx.run_project(config)
        xilinx.bit2mcs(config)
        xilinx.copy_firmware(config)
    if arguments.mcs:
        xilinx.bit2mcs(config)
        xilinx.copy_firmware(config)
    if arguments.upload:
        # TODO: i'm not sure
        xilinx.copy_firmware(config)
        publisher.publish(config)

if __name__ == '__main__':
    print('test')
