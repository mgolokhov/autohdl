from xml.dom import minidom
import os
import sys
import string
from hdlLogger import *

  

tools = {'avhdl'    : {'gui'   : 'avhdl.exe',
                       'batch' : None,
                       'path'  : ['Program Files/Aldec/', 'Aldec/']},
         'ise'      : {'gui'   : 'ise.exe',
                       'batch' : 'xtclsh.exe',
                       'path'  : ['Xilinx/', 'Program Files/Xilinx/']},
         'synplify' : {'gui'   : 'synplify_premier.exe',
                       'batch' : 'synplify_premier.exe',
                       'path'  : ['Program Files/Synplicity/', 'Synplicity/']}
         }
  
    
    
def appendTool(tag):
  log.debug('def appendTool<= tag='+tag)
  # search on hdd
  if not trySearch(tag):
    return # unsuccessful
  #if xml exists append
  #  else create new
  if os.path.exists(path_toolchain_xml):
    dom = minidom.parse(path_toolchain_xml)
  else:
    dom = minidom.parseString('<toolchain></toolchain>')
    
  # BUGAGA: append to head of nodes
  x = dom.createElement(tag)
  txt = dom.createTextNode(path) 
  x.appendChild(txt) 
  dom.firstChild.appendChild(x)
  
  f = open(path_toolchain_xml, 'w')
  f.write(dom.toxml())
  f.close() 
  

def appendToolToXml(tag, path):
  pathPredef = os.getcwd() + '/../resource'
  if not os.path.exists(pathPredef):
    log.warning('Can\'t find: ' + pathPredef + '; as the result no toolchain.xml generation...')
    return  
  
  pathToolchainXml = os.getcwd() + '/../resource/toolchain.xml'
  if not os.path.exists(pathToolchainXml):
    log.info('Generating new file: ' + pathToolchainXml)
    dom = minidom.parseString('<toolchain></toolchain>')
  else:
    dom = minidom.parse(pathToolchainXml)
  
  # BUGAGA: append to head of nodes
  x = dom.createElement(tag)
  txt = dom.createTextNode(path) 
  x.appendChild(txt) 
  dom.firstChild.appendChild(x)
  
  f = open(pathToolchainXml, 'w')
  f.write(dom.toxml())
  f.close() 
  

def parseXml(tag, pathToolchainXml):
  log.debug('def getPathFromXml<= tag'+str(tag)+' pathToolchainXml='+pathToolchainXml)
  dom = minidom.parse(pathToolchainXml)
  path = dom.getElementsByTagName(tag)
  for i in path:
    if os.path.exists(i.childNodes[0].toxml().strip()):
      return i.childNodes[0].toxml().strip()


def getPathFromXml(tag):
  '''
  Precondition: predefined design structure, current directory - /script;
  '''
  log.debug('def getPathFromXml<= tag='+tag)
  pathToolchainXml = os.getcwd() + '/../resource/toolchain.xml'
  if not os.path.exists(pathToolchainXml):
    log.info('No file: ' + pathToolchainXml)  
    return
  path = parseXml(tag, pathToolchainXml)
  return path


def searchTool(tag):
  global tools
  tool, mode = tag.split('_')
  toolExe = tools[tool][mode]
  if not toolExe:
    return None
    
  toolPaths = tools[tool]['path']
  drives = getDrivesList() # BUGAGA: win specific
  #first shoot
  for drive in drives:
    for toolPath in toolPaths:
      path = search(toolExe, drive+'/'+toolPath)
      if path:
        appendToolToXml(tag, path)
        return path
  #heavy artillery    
  for drive in drives:
    path = search(toolExe, drive)
    if path:
      appendToolToXml(tag, path)
      return path
  

def getPath(tag):
  '''
  Input: tag - toolName_mode, (e.g. ise_gui, ise_batch);
  Output: path to that tool; 
  '''
  log.debug('def getPath<= tag='+str(tag))
  
  path = getPathFromXml(tag)
  
  if not path:
    path = searchTool(tag) 
  
  return path





def search(exe_name, path):
  log.debug('def search<= exe_name='+exe_name+' path='+path)
  for root, dirs, files in os.walk(path): #@UnusedVariable
    for i in files:
#      print root+'/'+i
      if i == exe_name:
        return '/'.join([root.replace('\\','/'), i])


def getDrivesList():
  log.debug('def getDrivesList<=')
  drives_list = []
  for i in string.ascii_uppercase:
    if os.path.exists(i+':/'):
      drives_list.append(i+':/')
  log.debug('def getDrivesList=> drives_list='+str(drives_list))
  return drives_list



if __name__ == '__main__':
  

  avhdl_batch    = getPath('avhdl_batch')
  avhdl_gui      = getPath('avhdl_gui')
  synplify_gui   = getPath('synplify_gui')
  synplify_batch = getPath('synplify_batch')
  ise_gui        = getPath('ise_gui')
  ise_batch      = getPath('ise_batch')
  print 'avhdl_batch ', avhdl_batch
  print 'avhdl_gui ', avhdl_gui
  print 'synplify_gui ', synplify_gui
  print 'synplify_batch ', synplify_batch
  print 'ise_gui ', ise_gui
  print 'ise_batch ', ise_batch
  

