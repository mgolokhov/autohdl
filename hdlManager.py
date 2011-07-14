import argparse
import os
import sys

import instance
import structure
import build
import synthesis
import aldec
import implement

from hdlLogger import log_call, logging
log = logging.getLogger(__name__)

# TODO: convert ucf file name to full path

def validateTop(iTop):
  if not iTop:
    return False
  srcFiles = structure.search(iPath='../src', iOnly=['\.v$'], iIgnore=['\.svn', '\.git'])
  parsed = instance.parseFilesMultiproc(srcFiles)
  if parsed.get(iTop):
    return True


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


def getValidTop(iTopFromArg, iTopFromScript):
  try:
    topAsScriptName = os.path.splitext(os.path.basename(sys.modules['__main__'].__file__))[0]
  except AttributeError as e:
    logging.debug(e)
    topAsScriptName = ''

  if validateTop(iTopFromArg):
    top = iTopFromArg
    logging.info('Using top module name from arguments list')
  elif validateTop(iTopFromScript):
    top = iTopFromScript
    logging.info('Using top module name from script')
  elif topAsScriptName and validateTop(topAsScriptName):
    top = topAsScriptName
    logging.info('Using top module name same as script name')
  else:
    top = build.getParam(iKey='toplevel')
    if not validateTop(top):
      logging.error('Top module name undefined!')

  return top


def getValidUcf(iUcfFromArg, iUcfFromScript, iValidTop):
  ucfFromArg = getFullPathToUcf(iUcfFromArg)
  if ucfFromArg:
    logging.info('Using ucf file from argument list')
    return ucfFromArg

  ucfFromScript = getFullPathToUcf(iUcfFromScript)
  if ucfFromScript:
    logging.info('Using ucf file from script')
    return ucfFromScript

  ucfNameAsTop = getFullPathToUcf(iValidTop)
  if ucfNameAsTop:
    logging.info('Using ucf name same as top module')
    return ucfNameAsTop

  ucfFromBuild = getFullPathToUcf(build.getParam('UCF'))
  if ucfFromBuild:
    return ucfFromBuild

  logging.warning('Ucf file undefined')


def kungfu(iTop = '', iUcf = '', iSize = ''):
  logging.info('Processing...')

  try: # for Active-hdl compatibility
    os.chdir(os.path.dirname(sys.modules['__main__'].__file__))
  except AttributeError as e:
    log.debug(e)

  parser = argparse.ArgumentParser(description='hdl cycles manager')
  parser.add_argument('-tb', action = 'store_true', help = 'export project to active-hdl')
  parser.add_argument('-syn', choices = ['gui', 'batch'], help = 'synthesis step')
  parser.add_argument('-impl', action='store_true', help = 'implementation step')
  parser.add_argument('-top', help = 'top module name')
  parser.add_argument('-ucf', help = 'name of constraint file')
  parser.add_argument('-size', type = int, help = 'flash size')
  parser.add_argument('-d', action = 'store_true', help = 'debug flag')

  res = parser.parse_args()

  top = getValidTop(iTopFromArg=res.top, iTopFromScript=iTop)
  ucf = getValidUcf(iUcfFromArg=res.ucf, iUcfFromScript=iUcf, iValidTop = top)
  size = (res.size or iSize) #or build.getParam()))


  logging.info(('\n'
                 + '#'*40 + ' Main design config ' + '#'*40 +
                '\n'
                'device     : {device}\n'
                'top module : {top}\n'
                'ucf        : {ucf}\n'
                'flash size : {size}\n'
                 + '#'*80 + '#'*len(' Main design config ') +
                '').format(device = build.getParam('device'),
                                    top = top,
                                    ucf = ucf,
                                    size = size))

  if res.d:
    sys.exit()


  if res.tb:
    aldec.export()
  elif res.syn == 'gui':
    synthesis.run(iTopModule=top, iMode='synplify_gui')
  elif res.syn:
    synthesis.run(iTopModule=top)
  elif res.impl:
    implement.run(iTopModule=top, iUCF=ucf, iFlashSize=size)
  else:
    synthesis.run(iTopModule=top)
    implement.run(iTopModule=top, iUCF=ucf, iFlashSize=size)



if __name__ == '__main__':
  print os.path.splitext('asss')

  