import argparse
import os
import subprocess
from autohdl import *

def main():
  parser = argparse.ArgumentParser(description='Helper to create designs')
  parser.add_argument('-help', action='store_true', help='extended documentation in browser')
  parser.add_argument('-n', '--name', dest='name', default='', help='set design name and create structure (default name - current directory)')
  parser.add_argument('-v', '--version', dest='version', action='store_true', help='display package version')
  parser.add_argument('-tb', action = 'store_true', help = 'export project to active-hdl')
  parser.add_argument('-git', help = 'creation/synchronization with webdav repo')
  args = parser.parse_args()

  if args.version:
    print 'autohdl version: ' + pkg_info.getVersion()
  elif args.help:
    doc.handler('index')
  elif args.tb:
    hdlManager.kungfu()
  elif args.git:
    config = build.loadDefault()
    git.handle(args.git, config)
  else:
    dsn = structure.Design(iName = args.name)
    git.initialize(args.name if args.name else '.')
    print dsn

if __name__ == '__main__':
  main()

  
