import argparse
import logging
import os
import pprint
import sys

import instance
import structure
import build
import synthesis
import aldec
import implement
import webdav


from hdlLogger import log_call
alog = logging.getLogger(__name__)

@log_call
def validateTop(iTop):
  if not iTop:
    return False
  srcFiles = structure.search(iPath='../src', iOnly=['\.v$'], iIgnore=['\.svn', '\.git'])
#  parsed = instance.parseFilesMultiproc(srcFiles)
  parsed = instance.get_instances(srcFiles)
#  pprint.pprint(parsed)
  if parsed.get(iTop):
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
  pattern = iUcf if os.path.splitext(iUcf)[1] == '.ucf' else iUcf+'\.ucf'
  ucfFiles = structure.search(iPath='../src', iOnly = [pattern])
  if ucfFiles:
   return ucfFiles[0].replace('\\', '/')


@log_call
def getValidTop(iTopFromArg, iTopFromScript):
  try:
    topAsScriptName = os.path.splitext(os.path.basename(sys.modules['__main__'].__file__))[0]
  except AttributeError as e:
    alog.debug(e)
    topAsScriptName = ''

  if validateTop(iTopFromArg):
    top = iTopFromArg
    alog.info('Using top module name from arguments list')
  elif validateTop(iTopFromScript):
    top = iTopFromScript
    alog.info('Using top module name from script')
  elif topAsScriptName and validateTop(topAsScriptName):
    top = topAsScriptName
    alog.info('Using top module name same as script name')
  else:
    top = build.getParam(iKey='toplevel')
    if not validateTop(top):
      alog.error('Top module name undefined!')

  return top


@log_call
def getValidUcf(iUcfFromArg, iUcfFromScript, iValidTop):
  ucfFromArg = getFullPathToUcf(iUcfFromArg)
  if ucfFromArg:
    alog.info('Using ucf file from argument list')
    return ucfFromArg

  ucfFromScript = getFullPathToUcf(iUcfFromScript)
  if ucfFromScript:
    alog.info('Using ucf file from script')
    return ucfFromScript

  ucfNameAsTop = getFullPathToUcf(iValidTop)
  if ucfNameAsTop:
    alog.info('Using ucf name same as top module')
    return ucfNameAsTop

  ucfFromBuild = getFullPathToUcf(build.getParam('UCF'))
  if ucfFromBuild:
    return ucfFromBuild

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
def kungfu(iTop = '', iUcf = '', iSize = '', iUpload = '', iDevice = ''):
  alog.info('Processing...')
  alog.debug(sys.argv)
  validateLocation()

  parser = argparse.ArgumentParser(description='hdl cycles manager')
  parser.add_argument('-tb', action = 'store_true', help = 'export project to active-hdl')
  parser.add_argument('-syn', nargs ='?', default = 'nope', choices = ['gui', 'batch'], help = 'synthesis step')
  parser.add_argument('-impl', action = 'store_true', help = 'implementation step')
  parser.add_argument('-upload', action = 'store_true', help = 'upload firmware to WebDav server')
  parser.add_argument('-top', help = 'top module name')
  parser.add_argument('-d', action = 'store_true', help = 'debug flag')

  res = parser.parse_args()
  #bugaga: doesnt have default choice
  if res.syn == 'nope':
    res.syn = None
  elif not res.syn:
    res.syn = 'gui'

  top = getValidTop(iTopFromArg=res.top, iTopFromScript=iTop)
  ucf = getValidUcf(iUcfFromArg=res.ucf, iUcfFromScript=iUcf, iValidTop = top)
  size = (res.size or iSize or build.getParam(iKey='size'))
  upload = True if (not res.tb and not res.syn and not res.impl
                    and (res.upload or iUpload or build.getParam('upload'))) else False


  config = build.load()
  config['topModule'] = top
  config['ucf'] = ucf
  config['size'] = size
  config['mode'] = 'synplify_gui' if res.syn_gui else 'synplify_batch'
  config['device'] = iDevice if iDevice else config['device']


  alog.info(('Main design settings:\n'
                 + '#'*40 +
                '\n'
                'device     : {device}\n'
                'top module : {top}\n'
                'ucf        : {ucf}\n'
                'flash size : {size}\n'
                'upload     : {upload}\n'
                 + '#'*40 +
                '').format(device = config['device'],
                                    top = top,
                                    ucf = ucf,
                                    size = size,
                                    upload = True if upload else False))

  if res.d:
    sys.exit()


  if res.tb:
    aldec.export()
    synthesis.run(config)
  elif res.impl:
    implement.run(iTopModule=config['topModule'], iUCF=config['ucf'], iFlashSize=config['size'])
  elif res.upload:
    pass
  else:
    synthesis.run(config)
    implement.run(iTopModule=config['topModule'], iUCF=config['ucf'], iFlashSize=config['size'])

  if upload:
    webdav.upload_fw('../implement/{0}.bit'.format(top))
    webdav.upload_fw('../implement/{0}.mcs'.format(top))


if __name__ == '__main__':
  d = {'a':1, 'b': '2'}
  d1 = {'a':33, 'c': '4'}
  d1[None] = 'dfdf'
  print d.update(d1)
  print d

  