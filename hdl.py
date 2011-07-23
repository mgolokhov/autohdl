import optparse
import subprocess
import os

#import logging
#log = logging.getLogger(__name__)
from autohdl import *



if __name__ == '__main__':
  parser = optparse.OptionParser()
  parser.add_option('-t', '--test', action="store_true", dest='test', help = 'run unit tests')
#  parser.add_option('-l', '--log', action="store_true", dest='log', help = 'turn on logging')
  parser.add_option('-v', '--version', action="store_true", dest='version', help='package version')
  parser.add_option('-n', '--name', dest = 'name', default='',
                     help = 'set the name of a design (by default a current directory)')
  (options, args) = parser.parse_args()

#  if not options.log:
#    log.removeHandler(fileHandler)

  if options.test:
    #BUGAGA: correct paths
    #import autohdl.test.all_test
    pass
  elif options.version:
    print 'autohdl version: ' + pkg_info.getVersion()
  else:
    dsn = structure.Design(iName = options.name)
    print dsn
  


  

  
