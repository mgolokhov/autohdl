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
  

def checkStartPoint(iDirName):
  path = os.getcwd().replace('\\','/')
  if path.split('/')[-1] != iDirName:
    raise StructureException('[Project] Wrong start point.\n' \
                             'Expected: .../' + iDirName + \
                             ';\n Got: ' + path)  
  return path


# BUGAGA: genAndInit just temp stub
class Design(object):
  def __init__(self, iName = '', iPath = '', iIgnore = [], iOnly = [], genAndInit = True):
    if iPath:
      path = iPath
    else:
      path = os.getcwd()
    path = os.path.abspath(path).replace('\\','/')
    if not os.path.exists(path):
      log.error('Wrong rootPath ' + path)
    if iName:
      self._pathRoot = path+'/'+iName
      self._name     = iName
    else:
      self._pathRoot = path
      self._name     = path.split('/')[-1]

    self._filesMain  = []
    self._dirsMain   = []
    self._filesDep   = []
    
    if genAndInit:
      self.genPredef()
      self.initAll(iIgnore = iIgnore, iOnly = iOnly)


  @property
  def name(self):
    return self._name
  
  @property
  def pathRoot(self):
    return self._pathRoot
  
  def __str__(self):
    return \
    'DsnName: '       + self.name +\
    '\ndirMain:\n\t'  + '\n\t'.join(set(self._dirsMain)) +\
    '\nfileMain:\n\t' + '\n\t'.join(set(self._filesMain)) +\
    '\nfileDep:\n\t'  + '\n\t'.join(set(self._filesDep)) +\
    '\npathRoot:\n\t' + self._pathRoot
    
  def initAll(self, iOnly = [], iIgnore = []):
    self.initMain(iOnly = iOnly, iIgnore = iIgnore)
    self.initDep(iOnly = iOnly, iIgnore = iIgnore)
   
  def initMain(self,  iOnly = [], iIgnore = []):
    self._filesMain = []
    self._dirsMain = []
    for root, dirs, files in os.walk(self._pathRoot):
      r = root.replace('\\', '/')
      for f in files:
        fileFullPath = '%s/%s' % (r, f)
        if self.filter(iFiles = [fileFullPath], iOnly = iOnly, iIgnore = iIgnore): 
          self._filesMain.append(fileFullPath)
      for dir in dirs:
        d = '%s/%s' % (r, dir)
        if not os.listdir(d) and self.filter(iFiles = [d], iOnly = iOnly, iIgnore = iIgnore):
          self._dirsMain.append(d)
    return self._filesMain, self._dirsMain
  
  def initDep(self,  iOnly = [], iIgnore = []):
    self._filesDep = self.getDeps()
  
  def getLocToBuildXml(self, iPathSrcFile):
    log.debug('def getLocToBuildXml<= iPathSrcFile='+ iPathSrcFile)
    if not os.path.exists(iPathSrcFile):
      log.warning('Can\'t find file: ' + iPathSrcFile)
      return
    pathAsList = iPathSrcFile.replace('\\', '/').split('/')
    if pathAsList.count('src'):
      index = pathAsList.index('src')
    else:
      log.warning('Wrong location for source file: ' + iPathSrcFile)
      log.warning('Expecting in /src directory')
      return
    dsnName = pathAsList[(index-1)] # <dsnName>/src/
    rootPath = '/'.join(pathAsList[:index])
    pathBuildXml = '%s/%s' % (rootPath, 'resource')
    pathFull = pathBuildXml+'/build.xml'
    if not os.path.exists(pathFull):
      log.warning('Can\'t find ' + pathFull)
    return pathBuildXml, dsnName
    
  def getTree(self, iPathDeps, iIgnore = [], iOnly = []):
    log.debug('def getTree with iPathDeps='+str(iPathDeps)+' iIgnore='+str(iIgnore)+' iOnly='+str(iOnly))
    res = []
    for dep in iPathDeps:
      if os.path.isfile(dep):
        res.append(dep)
        continue
      for root, dirs, files in os.walk(dep):
        r = root.replace('\\', '/')
        for f in files:
          path = '%s/%s' % (r, f)
          res.append(path)
    if iIgnore or iOnly:
      res = self.filter(res, iIgnore, iOnly)
    return res
  
  def getDeps(self):
    log.debug('def getDeps<=')
    filesMain = self.getFileMain(iOnly = ['src'])
    files = set(filesMain)
    parsed = {}
    undef = set()
    dirBuildXmlPrev = ''
    dsnNamePrev = ''
    while(True):
      parsed, undef = instance.getUndef(files, parsed, undef)
      files = set()
      if not undef:
        break
      for i in undef: #set of tuples (pathFile, instance)
        afile = i[0]
        dirBuildXml, dsnName = self.getLocToBuildXml(afile)
        if dirBuildXmlPrev == dirBuildXml and dsnNamePrev == dsnName:
          continue
        else:
          dirBuildXmlPrev, dsnNamePrev = dirBuildXml, dsnName
        depsDic = build.getDeps(iDsnName = dsnName,
                                iBuildFile = dirBuildXml+'/build.xml')
        if not depsDic:
          log.info('Build.xml read but no dependences for design: '+dsnName)
          continue
        deps = depsDic.get(dsnName)
        if not deps: 
          log.info('Build.xml read but no dependences for design: '+dsnName)
          continue
        aset = set(self.getTree(deps, iOnly = ['\.v', '\.vhdl', '\.vm', '\.hdl']))
        files.update(aset)
    allSrcFiles = set([parsed[i][0] for i in parsed])     
    depSrcFiles = allSrcFiles - set(filesMain)
    log.debug('def getDeps=> depSrcFiles='+str(depSrcFiles))
    return depSrcFiles
    

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
    log.info('Predefined generation done')
   
  def getFileMain(self, iIgnore = [], iOnly = []):
    return self.filter(self._filesMain, iIgnore, iOnly)
  
  def getFileDep(self, iIgnore = [], iOnly = []):
    return self.filter(self._filesDep, iIgnore, iOnly)
  
  def getDirMain(self, iIgnore = [], iOnly = []):
    return self.filter(self._dirsMain, iIgnore, iOnly)
        
  def filter(self, iFiles, iIgnore = [], iOnly = []):
    '''
    Precondition:
      iFiles should be a list even if there is one file;
      iIgnore and iOnly: lists of regexp
    '''
    log.debug('def filter with iFiles='+str(iFiles)+' iIgnore='+str(iIgnore)+' iOnly='+str(iOnly))
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
        log.debug('Only pattern; deleting ' + f)
        files.remove(f)
        continue
      
      for ignore in iIgnore:
        if re.search(ignore, f):
          if files.count(f):
            log.debug('Ignore pattern; deleting ' + f)
            files.remove(f)
          break
    log.debug('filter return='+str(files))
    return files

#BUGAGA: migrate to that one
def filter(iFiles, iIgnore = [], iOnly = []):
  '''
  Precondition:
    iFiles should be a list even if there is one file;
    iIgnore and iOnly: lists of regexp
  '''
  log.debug('def filter with iFiles='+str(iFiles)+' iIgnore='+str(iIgnore)+' iOnly='+str(iOnly))
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
      log.debug('Only pattern; deleting ' + f)
      files.remove(f)
      continue
    
    for ignore in iIgnore:
      if re.search(ignore, f):
        if files.count(f):
          log.debug('Ignore pattern; deleting ' + f)
          files.remove(f)
        break
  log.debug('filter return='+str(files))
  return files


def search(iPath = '.', iIgnore = [], iOnly = []):
  '''
    Search files by pattern.
    Input: path (by default current directory), ignore and only patterns (should be lists)
    Returns list of files.
  '''
  resFiles = []
  for root, dirs, files in os.walk(iPath):
#    r = root.replace('\\', '/')
    for f in files:
      fullPath = '%s/%s' % (root, f)
      fullPath = (os.path.abspath(fullPath)).replace('\\', '/')
      if filter(iFiles = [fullPath], iOnly = iOnly, iIgnore = iIgnore): 
        resFiles.append(fullPath)
  return resFiles

  