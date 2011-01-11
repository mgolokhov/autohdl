import re
import os
import shutil
import subprocess
import sys

import instance
import build
from hdlLogger import *


class StructureException(Exception):
  def __init__(self, iString):
    self.string = iString
  def __str__(self):
    return self.string


class Design(object):
  def __init__(self, iName = '', iPath = '.', iGen = True, iInit = True):
    path = os.path.abspath(iPath).replace('\\','/')
    if not os.path.exists(path):
      log.error('Wrong rootPath ' + path)
    if iName:
      self._pathRoot = path+'/'+iName
      self._name     = iName
    else:
      self._pathRoot = path
      self._name     = path.split('/')[-1]

    self._filesMain  = []
    self._dirsMain   = [] # BUGAGA: do i really need?
    self._filesDep   = []
    
    if iGen:
      self.genPredef()
    if iInit:
      self.init()


  @property
  def name(self):
    return self._name
  
  @property
  def pathRoot(self):
    return self._pathRoot

  @property
  def filesMain(self):
    return self._filesMain

  @filesMain.setter
  def filesMain(self, value):
    self._filesMain = value

  @property
  def filesDep(self):
    return self._filesDep
  
  @filesDep.setter
  def filesDep(self, value):
    return self._filesDep
  
  def init(self):
    self.initFilesMain()
    self.initFilesDep()

  def initFilesMain(self):
    self._filesMain = search(iPath = self.pathRoot, iOnly = ['\.v']) # BUGAGA: only verilog files
  
  def initFilesDep(self):
    self._filesDep = getDepSrc(iSrc = self.filesMain, iOnly = ['\.v'])
  
  def __str__(self):
    return \
    'DsnName: '       + self.name +\
    '\npathRoot:\n\t' + self.pathRoot +\
    '\nfileMain:\n\t' + '\n\t'.join(self.filesMain) +\
    '\nfileDep:\n\t'  + '\n\t'.join(self.filesDep)

  def _copyFiles(self):
    '''
    Copy data files to predefined destinations
    '''
    log.debug('def _copyFiles')
    pathData = os.path.dirname(__file__)

    pathDestination = '%s/%s/%s' % (self._pathRoot,'script','kungfu.py')
    if not os.path.exists(pathDestination):
      shutil.copyfile('%s/%s' % (pathData,'data/kungfu.py'), pathDestination)
    
    pathDestination = '%s/%s/%s' % (self._pathRoot,'resource','synthesis_default') 
    if not os.path.exists(pathDestination):
      shutil.copyfile('%s/%s' % (pathData,'data/synthesis_default'), pathDestination)
    
    pathDestination = '%s/%s/%s' % (self._pathRoot,'resource','implement_default')
    if not os.path.exists(pathDestination):
      shutil.copyfile('%s/%s' % (pathData,'data/implement_default'), pathDestination)
  
  def genPredef(self):
    '''
    Generates predefined structure
    '''
    log.debug('def genPredef')
    predefined = ['src', 'TestBench', 'resource', 'script']
    for d in predefined:
      create = '%s/%s' % (self._pathRoot, d)
      if not os.path.exists(create):
        os.makedirs(create)
    self._copyFiles()
    build.genPredef(iPath = self.pathRoot+'/resource', iDsnName = self.name)
    log.info('Predefined generation done! PathRoot: '+self.pathRoot)
   
#
#############################################################
#

def filter(iFiles, iIgnore = [], iOnly = []):
  '''
  Precondition:
    iFiles should be a list even if there is one file;
    iIgnore and iOnly: lists of regexp
  '''
  log.debug('def filter IN iFiles='+str(iFiles)+' iIgnore='+str(iIgnore)+' iOnly='+str(iOnly))
  if not iIgnore and not iOnly:
    return iFiles
  
  files = iFiles[:]
  
  for f in iFiles:
    log.debug('current file ' + f)
    delete = True
    for only in iOnly:
      if re.search(only, f):
        delete = False
        break
    if iOnly and delete:
      log.debug('Only pattern - ignoring: ' + f)
      files.remove(f)
      continue
    
    for ignore in iIgnore:
      if re.search(ignore, f):
        if files.count(f):
          log.debug('Ignore pattern - ignoring ' + f)
          files.remove(f)
        break
  log.debug('def filter OUT files='+str(files))
  return files


def search(iPath = '.', iIgnore = [], iOnly = []):
  '''
    Search files by pattern.
    Input: path (by default current directory), ignore and only patterns (should be lists)
    Returns list of files.
  '''
  log.debug('def search IN iPath='+iPath+' iIgnore='+str(iIgnore)+' iOnly='+str(iOnly))
  resFiles = []
  for root, dirs, files in os.walk(iPath):
    for f in files:
      fullPath = '%s/%s' % (root, f)
      fullPath = (os.path.abspath(fullPath)).replace('\\', '/')
      if filter(iFiles = [fullPath], iOnly = iOnly, iIgnore = iIgnore): 
        resFiles.append(fullPath)
  log.debug('def search OUT resFiles='+str(resFiles))
  return resFiles


def getLocToBuildXml(iPathFile):
  '''
    Input:  path to file in some dsn;
    Output: tuple (path to build.xml, dsn_name);
  '''
  log.debug('def getLocToBuildXml IN iPathFile='+ iPathFile)
#  log.info('Searching build.xml for file: '+iPathFile)
  if not os.path.exists(iPathFile):
    log.warning("Can't find file: " + iPathFile)
    return
  pathAsList = iPathFile.replace('\\', '/').split('/')
  if pathAsList.count('src'):
    index = pathAsList.index('src')
  else:
    log.warning('Wrong location for source file: ' + iPathFile)
    log.warning('Expecting in <dsn_name>/src/ directory')
    return
  rootPath = '/'.join(pathAsList[:index])
  pathBuildXml = '%s/%s/%s' % (rootPath, 'resource', 'build.xml')
  if not os.path.exists(pathBuildXml):
    log.warning("Can't find " + pathBuildXml)
  dsnName = pathAsList[(index-1)] # <dsnName>/src/
  log.debug('def getLocToBuildXml OUT pathBuildXml='+str(pathBuildXml)+' dsnName='+str(dsnName))
  return pathBuildXml, dsnName


def getFilesFromXml(iUndefInst, iIgnore = [], iOnly = []):
  '''
    Input: undefined instances as a dictionary
      {key=instance name, value=path to file where it was instanced};
    Output: list of path to possible files;
  '''
  log.debug('def getFilesFromXml IN iUndefInst='+str(iUndefInst)+' iIgnore='+str(iIgnore)+' iOnly='+str(iOnly))
  possibleFiles = set()
  for afile in set(iUndefInst.values()):
    dirBuildXml, dsnName = getLocToBuildXml(afile)
    depsDic = build.getDeps(iDsnName = dsnName,
                            iBuildFile = dirBuildXml)
    if not depsDic or not depsDic.get(dsnName):
      log.info('File read but no dependences for design: '+dsnName+' in file: '+dirBuildXml)
      continue
    for path in depsDic.get(dsnName):
      possibleFiles.update(search(iPath = path, iIgnore = iIgnore, iOnly = iOnly))
  log.debug('def getFilesFromXml OUT possibleFiles='+str(possibleFiles))
  return list(possibleFiles)
    
      
def getDepSrc(iSrc, iIgnore = [], iOnly = []):
  log.debug('def getDepSrc IN iSrc='+str(iSrc)+' iIgnore='+str(iIgnore)+' iOnly='+str(iOnly))
  files = set(iSrc)
  parsed = {}
  undef = {}
  while(True):
    undefNew = instance.analyze(iPathFiles = files,
                                ioParsed = parsed,
                                iUndefInst = undef)
    
    if not (undefNew.viewkeys() ^ undef.viewkeys()): 
      for inst in undefNew:
        log.warning('Undefined instance: '+inst+'; in file: '+undefNew[inst])
      break
    if undefNew:
      files = getFilesFromXml(iUndefInst = undefNew, iIgnore = iIgnore, iOnly = iOnly)
    else:
      break
    undef = undefNew
    
  allSrcFiles = set([parsed[module][0] for module in parsed])     
  depSrcFiles = allSrcFiles - set(iSrc)
  log.debug('def getDepSrc OUT depSrcFiles='+str(depSrcFiles))
  return depSrcFiles 



