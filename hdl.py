import argparse
from autohdl import *
import autohdl.test.functional as atests



if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Helper to create designs')
  parser.add_argument('-n', '--name', dest='name', default='', help='set design name and create structure (default name - current directory)')
  parser.add_argument('-v', '--version', dest='version', action='store_true', help='display package version')
  parser.add_argument('-t', '--test', dest='test', action='store_true', help='run tests')
  args = parser.parse_args()

  if args.test:
    atests.run()
    print 'not yet'
  elif args.version:
    print 'autohdl version: ' + pkg_info.getVersion()
  else:
    dsn = structure.Design(iName = args.name)
    print dsn
  


  

  
