import re
import os
import shutil
import subprocess
import sys

import instance
import build
import hdlGlobals
from hdlLogger import *


class StructureException(Exception):
  def __init__(self, iString):
    self.string = iString
  def __str__(self):
    return self.string


gPredefined = ['src', 'TestBench', 'resource', 'script']


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
    self._filesDep = value
  
  def init(self):
    self.initFilesMain()
    self.initFilesDep()

  def initFilesMain(self):
    pass
#    ext = build.getSrcExtensions(iTag = 'synthesis_ext', iBuildFile = self.pathRoot)
#    only = ['/src/.*?\.'+i+'$' for i in ext]
#    self._filesMain = search(iPath = self.pathRoot, iOnly = only) 
  
  def initFilesDep(self):
    pass
#    ext = build.getSrcExtensions(iTag = 'synthesis_ext', iBuildFile = self.pathRoot)
#    only = ['\.'+i+'$' for i in ext]
#    self._filesDep = getDepSrc(iSrc = self.filesMain, iOnly = only)
  
  def __str__(self):
    structure = []
    for d in os.listdir(self.pathRoot):
      if d in gPredefined:
        structure.append('\t' + d)
#      if d not in gPredefined:
#        structure.append(d+' -external')
#        continue

        for root, dirs, files in os.walk(d):
          for d in dirs:
            adirectory = os.path.join(root, d)
            if filter(iFiles = adirectory, iIgnore = hdlGlobals.ignore):
              structure.append('\t\t' + d)
          for f in files:
            afile = os.path.join(root, f)
            if filter(iFiles = [afile], iIgnore = hdlGlobals.ignore):
              structure.append('\t\t' + f)

    return \
    'Design name: '       + self.name +\
    '\nRoot path:\n\t' + self.pathRoot +\
    '\nStructure:\n'    + '\n'.join(structure) +\
    '\nfileMain:\n\t' + '\n\t'.join(self.filesMain) +\
    '\nfileDep:\n\t'  + '\n\t'.join(self.filesDep)
    

  pathData = os.path.dirname(__file__)
  
  def _copyFile(self, iDestination):
    pathDestination = os.path.join(self._pathRoot, iDestination)
    pathSource = os.path.join(self.pathData, 'data', os.path.split(iDestination)[1])
    if not os.path.exists(pathDestination):
      shutil.copyfile(pathSource, pathDestination)
  
  def _copyFiles(self):
    '''
    Copy data files to predefined destinations
    '''
    log.debug('def _copyFiles')

    listToCopy = ['script/kungfu.py',
#                  'resource/synthesis_default',
#                  'resource/implement_default',
                  'resource/build.yaml']
    for l in listToCopy:
      self._copyFile(iDestination = l)

  
  def genPredef(self):
    '''
    Generates predefined structure
    '''
    log.debug('def genPredef')
    for d in gPredefined:
      create = '%s/%s' % (self._pathRoot, d)
      if not os.path.exists(create):
        os.makedirs(create)
    self._copyFiles()
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
  # make a list if there is one file
  if type(iFiles) == type(''):
    iFiles = [iFiles]
  
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


def search(iPath = '.', iIgnore = None, iOnly = None):
  '''
    Search files by pattern.
    Input: path (by default current directory), ignore and only patterns (should be lists)
    Returns list of files.
  '''
  log.debug('def search IN iPath='+iPath+' iIgnore='+str(iIgnore)+' iOnly='+str(iOnly))
  ignore = iIgnore or []
  only = iOnly or []
  resFiles = []
  if os.path.isfile(iPath):
    fullPath = (os.path.abspath(iPath)).replace('\\', '/')
    if filter(iFiles = [fullPath], iOnly = only, iIgnore = ignore): 
      resFiles.append(fullPath)
  else:  
    for root, dirs, files in os.walk(iPath):
      for f in files:
        fullPath = '%s/%s' % (root, f)
        fullPath = (os.path.abspath(fullPath)).replace('\\', '/')
        if filter(iFiles = fullPath, iOnly = only, iIgnore = ignore): 
          resFiles.append(fullPath)
  log.debug('def search OUT resFiles='+str(resFiles))
  return resFiles


def getDepSrc(iSrc, iIgnore = None, iOnly = None):
  log.debug('def getDepSrc IN iSrc='+str(iSrc)+' iIgnore='+str(iIgnore)+' iOnly='+str(iOnly))
  iIgnore = iIgnore or []
  iOnly = iOnly or []
  only = ['\.v']#build.getSrcExtensions(iTag = 'dep_parse_ext')
  only += iOnly
  
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
#      files = getFilesFromXml(iUndefInst = undefNew, iIgnore = iIgnore, iOnly = only)
      depTree = build.getDepTree(undefNew.values())
      files = filter(depTree, iIgnore = iIgnore, iOnly = only)
    else:
      break
    undef = undefNew
    
  allSrcFiles = set([parsed[module][0] for module in parsed])     
  depSrcFiles = allSrcFiles - set(iSrc)
  log.debug('def getDepSrc OUT depSrcFiles='+str(depSrcFiles))
  return depSrcFiles 



