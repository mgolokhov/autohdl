import argparse
import copy
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
from autohdl import webdav


from hdlLogger import log_call

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
    ucfFiles = structure.search(directory='../src', onlyExt = ['.ucf'])
  print ucfFiles
  if ucfFiles:
   return ucfFiles[0].replace('\\', '/')


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
  elif validateTop(config.get('top'), config):
    alog.info('Using top module name from script')
  elif topAsScriptName and validateTop(topAsScriptName, config):
    config['top'] = topAsScriptName
    alog.info('Using top module name same as script name')
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

  ucfNameAsTop = getFullPathToUcf(config['top'])
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
    if not {'script', 'src'}.issubset(os.listdir(os.getcwd()+'/..')):
      mayBe = os.path.dirname(sys.modules['__main__'].__file__)
      if {'script', 'src'}.issubset(os.listdir(mayBe+'/..')):
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
def setUpload(arguments, config):
  config['upload'] = True if (not arguments.tb and not arguments.syn and not arguments.impl
                              and (arguments.upload or config['upload'])) else False


@log_call
def printInfo(config):
  alog.info(('Main design settings:\n'
                 + '#'*40 +
                '\n'
                'device     : {device}\n'
                'top module : {top}\n'
                'ucf        : {ucf}\n'
                'PROM size  : {size} kilobytes\n'
                'upload     : {upload}\n'
                 + '#'*40 +
                '').format(device = config['device'],
                           top = config['top'],
                           ucf = config['ucf'],
                           size = config['size'],
                           upload = config['upload']))


@log_call
def kungfu(**configScript):
  alog.info('Processing...')
  alog.debug('args: '+ str(sys.argv))
  alog.debug('config: ' + str(configScript))

  validateLocation()
  configBuild = build.load(cacheEnable=False)
  build.dump(configBuild)
  config = mergeConfig(configScript, configBuild)

  parser = argparse.ArgumentParser(description='HDL Manager')
  parser.add_argument('-tb', action = 'store_true', help = 'export project to active-hdl')
  parser.add_argument('-top', help = 'top module name')
  parser.add_argument('-syn', nargs ='?', const = 'batch', help = 'synthesis step')
  parser.add_argument('-impl', action = 'store_true', help = 'implementation step')
  parser.add_argument('-mcs', nargs = '?', const = 'config', help = 'generate .mcs from .bit file')
  parser.add_argument('-upload', action = 'store_true', help = 'upload firmware to WebDav server')
  parser.add_argument('-d', action = 'store_true', help = 'debug flag')
  arguments = parser.parse_args()


  setValidTop(arguments, config)
  setValidUcf(config)
  setUpload(arguments, config)
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

  if config['upload']:
    #TODO: refactor
    webdav.upload_fw('{0}/{1}.bit'.format(implementPath, config['top']), config = config)
    webdav.upload_fw('{0}/{1}.mcs'.format(implementPath, config['top']), config = config)
    git.synchWithBuild(config)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='hdl cycles manager')
  parser.add_argument('-tb', help = 'export project to active-hdl')
  print parser.parse_args('-tb bka-dflkdjfd'.split())

  