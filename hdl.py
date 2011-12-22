import argparse
import logging
import pprint
import subprocess

alog = logging.getLogger(__name__)

import autohdl.build as build
import autohdl.structure as structure
import autohdl.git as git
import autohdl.hdlManager as hdlManager
import autohdl.pkg_info as pkg_info
import autohdl.doc as doc
import sys

def main():
  parser = argparse.ArgumentParser(parents=[git.commands()], description='Helper to create designs')
  parser.add_argument('-doc', action='store_true', help='extended documentation in browser')
  parser.add_argument('-n', '--name', dest='name', default='', help='set design name and create structure (default name - current directory)')
  parser.add_argument('-v', '--version', dest='version', action='store_true', help='display package version')
  parser.add_argument('-tb', action = 'store_true', help = 'export project to active-hdl')
#  parser.add_argument('-git', help = 'creation/synchronization with webdav repo; more info type -git doc')
  #TODO: choices
  parser.add_argument('-edit', choices = ['default_build'], help = 'edit default build.yaml file')
  args = parser.parse_args()

  if args.version:
    print 'autohdl version: ' + pkg_info.getVersion()
  elif args.doc:
    doc.handler('index')
  elif args.tb:
    hdlManager.kungfu()
  elif args.git:
    config = build.loadUncached(iBuildFile='resource/build.yaml', silent = True)
    if not config:
      alog.info('Using default build.yaml (to see content: hdl.py -edit default_build)')
      config = build.loadDefault()
    config.update({'git':args.git})
    git.handle(config)
  elif args.edit == 'default_build':
    subprocess.Popen('notepad {}/Lib/site-packages/autohdl/data/build.yaml'.format(sys.prefix))
  else:
    dsn = structure.Design(iName = args.name)
    git.initialize(args.name if args.name else '.')
    print dsn

if __name__ == '__main__':
  main()

  
