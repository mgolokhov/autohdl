from xml.dom import minidom
import xml
import os
import sys
import string
import glob

from hdlLogger import log_call, logging
log = logging.getLogger(__name__)  

import lib.yaml as yaml
from lib.yaml.error import YAMLError

class ToolchainException(Exception):
  def __init__(self, iString):
    self.string = iString
  def __str__(self):
    return self.string

  
  
class Tool(object):
  def __init__(self, iTag):
    
    try:
      self.tool, self.mode = iTag.split('_')
      self.tag = iTag
    except ValueError as exp:
      raise ToolchainException ('Invalid tag format. Tag= {0}; ({1})'.format(iTag, exp))
    
    self.data = {'avhdl'    : {'gui'   : 'avhdl.exe',
                               'batch' : None,
                               'path'  : ['/Aldec/']},
                 'ise'      : {'gui'   : 'ise.exe',
                               'batch' : 'xtclsh.exe',
                               'xflow' : 'xflow.exe',
                               'promgen': 'promgen.exe',
                               'path'  : ['/Xilinx/']},
                 'synplify' : {'gui'   : 'synplify_premier.exe',
                               'batch' : 'synplify_premier.exe',
                               'path'  : ['/Synopsys/', '/Synplicity/']}
                 }
    try:
      self.utilName = self.data[self.tool][self.mode]
    except KeyError as exp:
      raise ToolchainException('Cannot find tag in database. Tag= {0}; ({1})'.format(iTag, exp))

    self.pathCfg = sys.prefix + '/Lib/site-packages/autohdl_cfg/toolchain.yaml'
    self.cfg = dict()
    if not self.getFromCfg():
      self.searchLight()
    
  def getFromCfg(self):
    try:
      with open(self.pathCfg, 'r') as f:
        self.cfg = yaml.load(f)
    except (IOError, YAMLError) as exp:
      log.debug(exp)
      return False    
    
    if not self.cfg:
      return False
    
    try:
      path = self.cfg[self.tag]
    except KeyError as exp:
      log.debug(exp)
      return False
    
    if os.path.exists(path):
      self.result = path
      return True

    return False  

  def searchBrutal(self):
    for root, dirs, files in os.walk(path): #@UnusedVariable
      for i in files:
        log.info('Searching: '+root+'/'+i)
        if i == self.utilName:
          path = '/'.join([root.replace('\\','/'), i])
          return path    
    

  def searchLight(self):
    logicDrives = [i for i in string.ascii_uppercase if os.path.exists('{0}:/'.format(i))]
    try:
      paths = self.data[self.tool]['path']
    except KeyError as exp:
      raise ToolchainException('Cannot find tag in database. Tag= {0}; ({1})'.format(iTag, exp))
    rootDirs = []
    for logicDrive in logicDrives:
      for path in paths:
        for nested in ['', '/*/', '/*/'*2, '/*/'*3]: 
          log.info('Searching {}...'.format(self.tag)) 
          rootDirs += glob.glob('{drive}:{nested}{path}'.format(drive=logicDrive, nested=nested, path=path))
    self.fullPaths = []
    for i in rootDirs:
      for nested in ['', '/*/', '/*/'*2, '/*/'*3, '/*/'*4, '/*/'*5, '/*/'*6]:
        log.info('Searching {}...'.format(self.tag)) 
        self.fullPaths += glob.glob('{0}{1}{2}'.format(i, nested, self.utilName))
    
    if self.fullPaths:
      self.fullPaths = [i.replace('\\', '/') for i in self.fullPaths]
      self.fullPaths.sort(cmp=None, key=os.path.getmtime, reverse=True)
      self.askConfirm()
      self.saveSearchResult()
           

  def saveSearchResult(self):
    try:
      if not self.cfg:
        self.cfg = dict()
      with open(self.pathCfg, 'w') as f:
        self.cfg.update({self.tag: '{}'.format(self.result)})
        yaml.dump(self.cfg, f, default_flow_style=False)
    except (IOError, YAMLError) as exp:
      log.error(exp)
      return


  def askConfirm(self):
    d = dict([(index, path) for index, path in enumerate(self.fullPaths)])
    current = 0
    while True:
      print '\nFound paths (in use [*]):'
      for k, v in d.iteritems():
        if current == k:
          print '[*] {}'.format(v)
        else: 
          print '[{0}] {1}'.format(k, v)
      num = raw_input('To change enter number. Leave as is and continue hit Enter:')
      if not num:
        self.result = d[current]
        return
      try:
        if int(num) <= len(d):
          current = int(num) 
      except ValueError as exp:
        log.debug(exp)
        print 'Invalid input!'



def getPath(iTag):
  return Tool(iTag).result
        

if __name__ == '__main__':
  print Tool('avhdl_gui').result
  print Tool('synplify_batch').result
  print Tool('synplify_gui').result
  print Tool('ise_gui').result
  print Tool('ise_batch').result
  print Tool('ise_xflow').result
#  getPath('avhdl_gui')
#  getPath('synplify_batch')
#  getPath('synplify_gui')
#  getPath('ise_gui')
#  getPath('ise_batch')
#  getPath('ise_xflow')

