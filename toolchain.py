from xml.dom import minidom
import xml
import os
import sys
import string

from hdlLogger import log_call, logging
log = logging.getLogger(__name__)  

gTools = {'avhdl'    : {'gui'   : 'avhdl.exe',
                       'batch' : None,
                       'path'  : ['Program Files/Aldec/', 'Aldec/']},
         'ise'      : {'gui'   : 'ise.exe',
                       'batch' : 'xtclsh.exe',
                       'path'  : ['Xilinx/', 'Program Files/Xilinx/']},
         'synplify' : {'gui'   : 'synplify_premier.exe',
                       'batch' : 'synplify_premier.exe',
                       'path'  : ['Program Files/Synplicity/', 'Synplicity/']}
         }
  

class ToolchainException(Exception):
  def __init__(self, iString):
    self.string = iString
  def __str__(self):
    return self.string
    

@log_call
def refreshXml(iTag, path, iDirToolchainXml):
  log.debug('def refreshXml IN iTag='+iTag+'; path='+path)
  fileToolchainXml = iDirToolchainXml + 'toolchain.xml'
  
  if not os.path.exists(iDirToolchainXml):
    os.mkdir(iDirToolchainXml)      
  
  try:
    if os.path.exists(fileToolchainXml):
      dom = minidom.parse(fileToolchainXml)
    else:
      log.info('Generating new file: ' + fileToolchainXml)
      dom = minidom.parseString('<toolchain></toolchain>')      
  except xml.parsers.expat.ExpatError as e:
    log.error('Wrong xml format! file='+fileToolchainXml+'; details='+str(e))
    log.info('Generating new file: ' + fileToolchainXml)
    dom = minidom.parseString('<toolchain></toolchain>')
    
  # BUGAGA: append to head of nodes
  x = dom.createElement(iTag)
  txt = dom.createTextNode(path) 
  x.appendChild(txt) 
  dom.firstChild.appendChild(x)

  try:
    f = open(fileToolchainXml, 'w')
    f.write(dom.toxml())
  except IOError as e:  
    log.warning(e)
  finally:
    f.close() 
  
  
@log_call
def search(exe_name, path):
  for root, dirs, files in os.walk(path): #@UnusedVariable
    for i in files:
      log.info('Searching: '+root+'/'+i)
      if i == exe_name:
        path = '/'.join([root.replace('\\','/'), i])
        return path


@log_call
def getDrivesList():
  drives_list = []
  for i in string.ascii_uppercase:
    if os.path.exists(i+':/'):
      drives_list.append(i+':/')
  return drives_list


@log_call
def searchTool(iTag):
  '''
  '''
  global gTools
  tool, mode = iTag.split('_')
  toolExe = gTools[tool][mode]
  toolPaths = gTools[tool]['path']
  drives = getDrivesList() # BUGAGA: win specific, cd-drive
  log.info('Searching tool: '+toolExe)
  #first shoot
  for drive in drives:
    for toolPath in toolPaths:
      path = search(toolExe, drive+'/'+toolPath)
      if path:
        return path
  #heavy artillery    
  for drive in drives:
    path = search(toolExe, drive)
    if path:
      return path
  log.error("Can't find tool in system! executable="+toolExe+'; tag='+iTag)
#
# Trying to get info from configure file
#
@log_call
def parseXml(iTag, iPathToolchainXml):
  try:
    dom = minidom.parse(iPathToolchainXml)
  except xml.parsers.expat.ExpatError as e:
    log.error('Wrong xml format! file='+iPathToolchainXml+'; details='+str(e))
    return
  path = dom.getElementsByTagName(iTag)
  for i in path:
    # BUGAGA: first valid occurrence, should be checking latest version
    validPath = i.childNodes[0].toxml().strip()
    if os.path.exists(validPath):
      log.info('Got path from xml='+iPathToolchainXml+'; tag='+iTag)
      return validPath


@log_call
def getPathFromXml(iTag, iDirToolchainXml):
  '''
  Input: iTag - Tool Name mode, (e.g. ise_gui, ise_batch);
  Precondition: 
    predefined design structure;
    current directory - <design_name>/script;
  '''
  pathGlobalXml = iDirToolchainXml + 'toolchain.xml'
  if not os.path.exists(pathGlobalXml):
    log.info("Can't find configure file: " + pathGlobalXml)  
    return
  path = parseXml(iTag, pathGlobalXml)
  return path


@log_call
def validateTag(iTag):
  '''
  Checks tag is registered.
  Invalid tag - throws exceptions.
  '''
  path = os.getcwd()
  global gTools
  res = iTag.split('_')
  if len(res) != 2:
    raise ToolchainException('Invalid tag: '+iTag)
  tool, mode = res
  toolExe = None
  try:
    toolExe = gTools[tool][mode]
  except KeyError, e:
    # get exception value from tuple (exc_type, exc_value, exc_traceback)
    raise ToolchainException("Can't find key in database: "+str(sys.exc_info()[1])+' tag: '+iTag)
  if not toolExe:
    raise ToolchainException("No such tool in database; given tag: "+iTag)


  
@log_call
def getPath(iTag):
  '''
  Input:  iTag - Tool Name mode, (e.g. ise_gui, ise_batch);
  Output: path to that tool; 
  Throws exception if there is no path associated with a tool;
  '''
  path = None
  dirToolchainXml = sys.prefix + '/Lib/site-packages/autohdl_cfg/'
  try:
    validateTag(iTag)
    path = getPathFromXml(iTag = iTag, iDirToolchainXml = dirToolchainXml)
    if not path:
      path = os.path.abspath(searchTool(iTag)).replace('\\','/')
      if not path:
  #      log.error("Can't find tool in system. tag: "+iTag)
        raise ToolchainException("Can't find tool in system. tag: "+iTag)
      refreshXml(iTag = iTag, path = path, iDirToolchainXml = dirToolchainXml)
  except ToolchainException as e:
    log.error(e)
    raise e
  return path


if __name__ == '__main__':
  getPath('avhdl_gui')
#  getPath('avhdl_batch')
  getPath('synplify_batch')
  getPath('synplify_gui')
  getPath('ise_gui')
  getPath('ise_batch')

