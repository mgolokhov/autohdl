import argparse
from autohdl import *

def main():
  parser = argparse.ArgumentParser(description='Helper to create designs')
  parser.add_argument('-n', '--name', dest='name', default='', help='set design name and create structure (default name - current directory)')
  parser.add_argument('-v', '--version', dest='version', action='store_true', help='display package version')
  parser.add_argument('-t', '--test', dest='test', action='store_true', help='run tests')
  parser.add_argument('-tb', action = 'store_true', help='export in active-hdl')
  parser.add_argument('-git', nargs = '*', help='usage: hdl.py -git [src [addr]]')
  args = parser.parse_args()


  if args.test:
#    atests.run()
    pass
  elif args.tb:
    hdlManager.kungfu()
  elif args.git is not None:
    if len(args.git) > 2:
      print 'usage: hdl.py -git [src [addr]]'
    elif not args.git:
      webdav.git_init()
    elif len(args.git) == 1:
      webdav.git_init(args.git[0])
    elif len(args.git) == 2:
      webdav.git_init(args.git[0], args.git[1])
  elif args.version:
    print 'autohdl version: ' + pkg_info.getVersion()
  else:
    dsn = structure.Design(iName = args.name)
    print dsn
  


if __name__ == '__main__':
  main()

  
