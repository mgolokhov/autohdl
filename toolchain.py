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


gTools = {'avhdl'    : {'gui'   : 'avhdl.exe',
                       'batch' : None,
                       'path'  : ['/Aldec/']},
         'ise'      : {'gui'   : 'ise.exe',
                       'batch' : 'xtclsh.exe',
                       'xflow' : 'xflow.exe',
                       'path'  : ['/Xilinx/']},
         'synplify' : {'gui'   : 'synplify_premier.exe',
                       'batch' : 'synplify_premier.exe',
                       'path'  : ['/Synopsys/', '/Synplicity/']}
         }
  
  
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
    if not self.getFromCfg():
      self.search()
    
  def getFromCfg(self):
    try:
      with open(self.pathCfg, 'r') as f:
        self.cfg = yaml.load(f) or dict()
    except (IOError, YAMLError) as exp:
      log.error(exp)
      return False    
    
    if not self.cfg:
      return False
    
    try:
      possiblePaths = self.cfg[self.tag]['path']
    except KeyError as exp:
      log.debug(exp)
      return False
    
    for i in possiblePaths:
      if os.path.exists(i):
        self.path = i
        return True

    return False

  def searchBrutal(self):
    for root, dirs, files in os.walk(path): #@UnusedVariable
      for i in files:
        log.info('Searching: '+root+'/'+i)
        if i == self.utilName:
          path = '/'.join([root.replace('\\','/'), i])
          return path    
    

  def search(self):
    logicDrives = [i for i in string.ascii_uppercase if os.path.exists('{0}:/'.format(i))]
    try:
      paths = self.data[self.tool]['path']
    except KeyError as exp:
      raise ToolchainException('Cannot find tag in database. Tag= {0}; ({1})'.format(iTag, exp))
    guessStep1 = []
    for logicDrive in logicDrives:
      for path in paths:
        for nested in ['', '/*/', '/*/'*2, '/*/'*3]:  
          guessStep1 += glob.glob('{drive}:{nested}{path}'.format(drive=logicDrive, nested=nested, path=path))
    guessStep2 = []
    for i in guessStep1:
      for nested in ['', '/*/', '/*/'*2, '/*/'*3, '/*/'*4, '/*/'*5, '/*/'*6]:
        guessStep2 += glob.glob('{0}{1}{2}'.format(i, nested, self.utilName))
    
    print guessStep2
    
    if guessStep2:
      guessStep2.sort(cmp=None, key=os.path.getmtime, reverse=True)
      self.result = guessStep2[0]
      self.saveSearchResult(guessStep2)
           

  def saveSearchResult(self, iPaths):
    try:
      with open(self.pathCfg, 'w') as f:
        self.cfg.update({self.tag: iPaths})
        yaml.dump(self.cfg, f, default_flow_style=False)
    except (IOError, YAMLError) as exp:
      log.error(exp)
      return

#@log_call
#def refreshXml(iTag, path, iDirToolchainXml):
#  fileToolchainXml = iDirToolchainXml + 'toolchain.xml'
#  
#  if not os.path.exists(iDirToolchainXml):
#    os.mkdir(iDirToolchainXml)      
#  
#  try:
#    if os.path.exists(fileToolchainXml):
#      dom = minidom.parse(fileToolchainXml)
#    else:
#      log.info('Generating new file: ' + fileToolchainXml)
#      dom = minidom.parseString('<toolchain></toolchain>')      
#  except xml.parsers.expat.ExpatError as e:
#    log.error('Wrong xml format! file='+fileToolchainXml+'; details='+str(e))
#    log.info('Generating new file: ' + fileToolchainXml)
#    dom = minidom.parseString('<toolchain></toolchain>')
#    
#  # BUGAGA: append to head of nodes
#  x = dom.createElement(iTag)
#  txt = dom.createTextNode(path) 
#  x.appendChild(txt) 
#  dom.firstChild.appendChild(x)
#
#  try:
#    f = open(fileToolchainXml, 'w')
#    f.write(dom.toxml())
#  except IOError as e:  
#    log.warning(e)
#  finally:
#    f.close() 
#  
#  
#@log_call
#def search(exe_name, path):
#  for root, dirs, files in os.walk(path): #@UnusedVariable
#    for i in files:
#      log.info('Searching: '+root+'/'+i)
#      if i == exe_name:
#        path = '/'.join([root.replace('\\','/'), i])
#        return path
#
#
#@log_call
#def getDrivesList():
#  drives_list = []
#  for i in string.ascii_uppercase:
#    if os.path.exists('{0}:/'.format(i)):
#      drives_list.append(i+':/')
#  return drives_list
#
#
#@log_call
#def searchTool(iTag):
#  '''
#  '''
#  global gTools
#  tool, mode = iTag.split('_')
#  toolExe = gTools[tool][mode]
#  toolPaths = gTools[tool]['path']
#  drives = getDrivesList() # BUGAGA: win specific, cd-drive
#  log.info('Searching tool: '+toolExe)
#  #first shoot
#  for drive in drives:
#    for toolPath in toolPaths:
#      path = search(toolExe, drive+'/'+toolPath)
#      if path:
#        return path
#  #heavy artillery    
#  for drive in drives:
#    path = search(toolExe, drive)
#    if path:
#      return path
#  log.error("Can't find tool in system! executable="+toolExe+'; tag='+iTag)
##
## Trying to get info from configure file
##
#@log_call
#def parseXml(iTag, iPathToolchainXml):
#  try:
#    dom = minidom.parse(iPathToolchainXml)
#  except xml.parsers.expat.ExpatError as e:
#    log.error('Wrong xml format! file='+iPathToolchainXml+'; details='+str(e))
#    return
#  path = dom.getElementsByTagName(iTag)
#  for i in path:
#    # BUGAGA: first valid occurrence, should be checking latest version
#    validPath = i.childNodes[0].toxml().strip()
#    if os.path.exists(validPath):
#      log.info('Got path from xml='+iPathToolchainXml+'; tag='+iTag)
#      return validPath
#
#
#@log_call
#def getPathFromXml(iTag, iDirToolchainXml):
#  '''
#  Input: iTag - Tool Name mode, (e.g. ise_gui, ise_batch);
#  Precondition: 
#    predefined design structure;
#    current directory - <design_name>/script;
#  '''
#  pathGlobalXml = iDirToolchainXml + 'toolchain.xml'
#  if not os.path.exists(pathGlobalXml):
#    log.info("Can't find configure file: " + pathGlobalXml)  
#    return
#  path = parseXml(iTag, pathGlobalXml)
#  return path
#
#
#@log_call
#def validateTag(iTag):
#  '''
#  Checks tag is registered.
#  Invalid tag - throws exceptions.
#  '''
#  path = os.getcwd()
#  global gTools
#  res = iTag.split('_')
#  if len(res) != 2:
#    raise ToolchainException('Invalid tag: '+iTag)
#  tool, mode = res
#  toolExe = None
#  try:
#    toolExe = gTools[tool][mode]
#  except KeyError, e:
#    # get exception value from tuple (exc_type, exc_value, exc_traceback)
#    raise ToolchainException("Can't find key in database: "+str(sys.exc_info()[1])+' tag: '+iTag)
#  if not toolExe:
#    raise ToolchainException("No such tool in database; given tag: "+iTag)
#
#
#  
#@log_call
#def getPath(iTag):
#  '''
#  Input:  iTag - Tool Name mode, (e.g. ise_gui, ise_batch);
#  Output: path to that tool; 
#  Throws exception if there is no path associated with a tool;
#  '''
#  path = None
#  dirToolchainXml = sys.prefix + '/Lib/site-packages/autohdl_cfg/'
#  try:
#    validateTag(iTag)
#    path = getPathFromXml(iTag = iTag, iDirToolchainXml = dirToolchainXml)
#    if not path:
#      path = os.path.abspath(searchTool(iTag)).replace('\\','/')
#      if not path:
#  #      log.error("Can't find tool in system. tag: "+iTag)
#        raise ToolchainException("Can't find tool in system. tag: "+iTag)
#      refreshXml(iTag = iTag, path = path, iDirToolchainXml = dirToolchainXml)
#  except ToolchainException as e:
#    log.error(e)
#    raise e
#  return path


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

