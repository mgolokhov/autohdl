import argparse
import glob
import logging
import os
import pprint
import sys

from autohdl.hdlGlobals import implementPath
from autohdl import structure
from autohdl import build
from autohdl import git
from autohdl import synthesis
from autohdl import aldec
from autohdl import implement
import webdav

from autohdl.hdlLogger import log_call

alog = logging.getLogger(__name__)

@log_call
def validateTop(iTop, config):
    parsed = config.get('parsed')
    if not parsed:
        structure.setSrc(config)
        parsed = config['parsed']

    if iTop and parsed.get(iTop):
        return True


@log_call
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
    if os.path.splitext(iUcf)[1] == '.ucf':
        ucfFiles = glob.glob(iUcf)
    #  pattern = iUcf if os.path.splitext(iUcf)[1] == '.ucf' else iUcf+'.ucf'
    else:
        ucfFiles = structure.search(directory='../src', onlyExt=['.ucf'])
    if ucfFiles:
        for i in ucfFiles:
            if iUcf == os.path.splitext(os.path.basename(i))[0]:
                return i.replace('\\', '/')


@log_call
def setValidTop(arguments, config):
    try:
        topAsScriptName = os.path.splitext(os.path.basename(sys.modules['__main__'].__file__))[0]
    except AttributeError as e:
        alog.debug(e)
        topAsScriptName = ''

    if validateTop(arguments.top, config):
        config['top'] = arguments.top
        alog.info('Using top module name from arguments list')
    elif topAsScriptName and validateTop(topAsScriptName, config):
        config['top'] = topAsScriptName
        alog.info('Using top module name same as script name')
    elif validateTop(config.get('top'), config):
        alog.info('Using top module name from merged configs (build.yaml and script)')
    else:
        top = build.load().get('top')
        if validateTop(top, config):
            alog.info('Using top module from build.yaml')
            config['top'] = top
        else:
            alog.error('Top module name undefined!')


@log_call
def setValidUcf(config):
    ucfFromScript = getFullPathToUcf(config['ucf'])
    if ucfFromScript:
        config['ucf'] = ucfFromScript
        alog.info('Using ucf file from script')
        return

    top = config.get('top')
    if top:
        ucfNameAsTop = getFullPathToUcf(top)
        if ucfNameAsTop:
            config['ucf'] = ucfNameAsTop
            alog.info('Using ucf name same as top module')
            return

    ucfFromBuild = getFullPathToUcf(build.load().get('ucf'))
    if ucfFromBuild:
        config['ucf'] = ucfFromBuild
        alog.info('Using ucf file from build.yaml')
        return

    alog.warning('Ucf file undefined')


@log_call
def validateLocation():
    try: # for Active-hdl compatibility
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


@log_call
def mergeConfig(configScript, configBuild):
    """
    Rewrites all params in configBuild by configScript, except 'dep' (it extends);
    """
    depInScript = configScript.pop('dep', []) or []
    configBuild.update(configScript)
    if depInScript:
        configBuild['dep'] = depInScript + (configBuild.get('dep', []) or [])
    return configBuild


@log_call
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
               '').format(technology=config.get('technology'),
        part=config.get('part'),
        package=config.get('package'),
        top=config.get('top'),
        ucf=config.get('ucf'),
        size=config.get('size'),
        upload=config.get('upload')))


@log_call
def kungfu(**configScript):
    alog.info('Processing...')
    alog.debug('args: ' + str(sys.argv))
    alog.debug('config: ' + str(configScript))

    validateLocation()
    configBuild = build.load(cacheEnable=False)
    build.compare_global(configScript)
    build.compare_global(configBuild)
    build.dump(configBuild)
    config = mergeConfig(configScript, configBuild)

    parser = argparse.ArgumentParser(description='HDL Manager')
    parser.add_argument('-tb', action='store_true', help='export project to active-hdl')
    parser.add_argument('-top', help='top module name')
    parser.add_argument('-syn', nargs='?', const='batch', help='synthesis step')
    parser.add_argument('-impl', action='store_true', help='implementation step')
    parser.add_argument('-mcs', nargs='?', const='config', help='generate .mcs from .bit file')
    parser.add_argument('-upload', action='store_true', help='upload firmware to WebDav server')
    parser.add_argument('-git_mes', help='git message')
    parser.add_argument('-d', action='store_true', help='debug flag')
    arguments = parser.parse_args()

    setValidTop(arguments, config)
    setValidUcf(config)
    config['dsnName'] = os.path.basename(os.path.dirname(os.getcwd()))
    config['mode'] = 'synplify_gui' if arguments.syn == 'gui' else 'synplify_batch'
    if arguments.mcs and arguments.mcs != 'config': config['size'] = arguments.mcs

    if arguments.d:
        pprint.pprint(config)
        config['debug'] = True

    printInfo(config)

    if arguments.tb:
        aldec.export(config)
        return
    elif arguments.syn:
        synthesis.run(config)
    elif arguments.impl:
        implement.run(config)
    elif arguments.mcs:
        implement.bit2mcs(config)
        return
    elif arguments.upload:
        pass
    elif not config.get('debug'):
        synthesis.run(config)
        implement.run(config)

    if arguments.upload:
        config['git_mes'] = arguments.git_mes
        git.push_firmware(config)
        webdav.upload_fw(config=config)
#        pprint.pprint(config)


if __name__ == '__main__':
    print 'test'
  
