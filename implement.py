import os
import sys
import shutil
import re
import subprocess
import filecmp

import toolchain
import synthesis
import structure
import build
from hdlLogger import *





gSynToImpl = {'set_option -technology' :'project set family',
             'set_option -part'        :'project set device',
             'set_option -package'     :'project set package',
             'set_option -speed_grade' :'project set speed'
             }


def __addSpaces(iString):
  '''
  Util function. Adds in search pattern variable qty of whitespaces. 
  '''
  log.debug('def __addSpaces=> iString='+iString)
  l = iString.split()
  res = '\s+'.join(l) + '\s+'
  return res


def getContentImpl():
  '''
  Returns content of implement.tcl or
  default implementation script.
  '''
  log.debug('def getContentImpl=> ')
  pathCur = os.getcwd()
  pathImplementTcl = pathCur + '/implement.tcl'
  if os.path.exists(pathImplementTcl):
    f = open(pathImplementTcl, 'r')
  else:
    log.info('Getting parameters from default implementation script')
    f = open(pathCur + '/../resource/implement_default', 'r')
  content = f.read()
  f.close()
  return content


def getContentSyn():
  log.debug('def getContentSyn=> ')
  pathCur = os.getcwd()
  pathImplementTcl = pathCur+'/synthesis.prj'
  if os.path.exists(pathImplementTcl):
    f = open(pathImplementTcl, 'r')
  else:
    log.info('Getting parameters from default synthesis script')
    f = open(pathCur+'/../resource/synthesis_default', 'r')
  scriptContent = f.read()
  f.close()
  
  return scriptContent



def getParam(iParam, iScriptContent):
  '''
  Gets parameter from implement script.
  Returns tuple (full string, parameter).
  '''
  log.debug('def getParam=> iParam='+iParam+' iScriptContent=\n'+iScriptContent)
  param = __addSpaces(iParam)
  match = re.search(param+'(.+)', iScriptContent)
  res = match.group(), match.group(1)
  return res


def getPureFile(iSrc):
  '''
  Strip everything except file location.
  '''
  log.debug('def getPureFile=> iSrc='+iSrc)
  match = re.search(r'xfile\s+add\s+"([^"]+)"\s*#?', iSrc)
  return match.group(1).strip().strip('"')


def mergeSrc(iSrcFileSys, iSrcScript):
  '''
  Returns merged list with metadata.
  '''
  log.debug('def mergeSrc<= iSrcFileSys='+str(iSrcFileSys)+'iSrcScript='+str(iSrcScript))
  srcFileSys = iSrcFileSys[:]
  srcScript = iSrcScript[:]
  merged = []
  for src in srcScript:
    srcPure = getPureFile(src)
    if src.strip()[0] == '#':
      merged.append([src, 'comment'])
      if srcFileSys.count(srcPure):
        srcFileSys.remove(srcPure)
    elif srcPure in srcFileSys:
      merged.append([src, 'same'])
      srcFileSys.remove(srcPure)
    else:
      merged.append(['# ' + src + ' DELETED', 'del'])
      
  for src in srcFileSys:
    merged.append(['xfile add "' + src + '"', 'new'])
  log.debug('def mergeSrc=> merged='+str(merged))
  return merged


def refreshSrcInContent(iContent, iSrc):
  log.debug('def refreshSrcInContent=> iContent=\n'+iContent+' iSrc='+str(iSrc))
  contentImplNewList = iContent.split('\n')
  lastIndex = 0
  for line in contentImplNewList:
    if line.find('xfile') == -1:
      continue
    for i in iSrc:
      if i[0].find(line.strip()) != -1:
        lastIndex = contentImplNewList.index(line)
        contentImplNewList[contentImplNewList.index(line)] = i[0]
  
  if not lastIndex:
    lastIndex = 0
  
  for i in iSrc:
    if i[1] == 'new':
      contentImplNewList.insert(lastIndex+1, i[0])
      
  contentImplNew = '\n'.join(contentImplNewList)    
  return contentImplNew  


def removeComments(iScriptContentSyn):
  return re.sub('#.*', '', iScriptContentSyn)
  

def refreshParams(iScriptContentSyn, iScriptContentImpl, iDictionary):
  '''
  Synchronizes implement and synthesis scripts and src in file system.
  '''
  log.debug('def refreshParams=> iScriptContentSyn=\n'+iScriptContentSyn+'iScriptContentImpl=\n'+iScriptContentImpl+'iDictionary='+str(iDictionary))
  scriptContentImplNew = iScriptContentImpl
  iScriptContentSyn = removeComments(iScriptContentSyn)
  for key in iDictionary:
    paramNew = getParam(key, iScriptContentSyn)
    paramOld = getParam(iDictionary[key], iScriptContentImpl)
    paramToSet = (paramOld[0]).replace(paramOld[1], paramNew[1])
    scriptContentImplNew = scriptContentImplNew.replace(paramOld[0], paramToSet)
  
  srcFromFileSys = getSrcFromFileSys()
  srcFromScript = getSrcFromScript(iScriptContentImpl)
  
  resultSrc = mergeSrc(srcFromFileSys, srcFromScript)
  
  contentImplNew = refreshSrcInContent(scriptContentImplNew,
                                       resultSrc)
  return contentImplNew



def needResynthesis(iTopModule = ''):
  '''
  Check for necessity to run synthesis.
    Possible reasons:
      - can't find:
          - synthesis.prj file;
          - <TopModule>.edf file;
      - mismatch /synthesis/synthesis.prj and /script/synthesis.prj;
      - new TopModule name specified;
  '''
  pathCur = os.getcwd()
  log.debug('def needResynthesis=> iTopModule='+iTopModule)
  
  pathSynthesisPrj = pathCur + '/../synthesis/synthesis.prj'
  pathSynthesisPrjEditable = pathCur + '/synthesis.prj'
  if not os.path.exists(pathSynthesisPrj) or not os.path.exists(pathSynthesisPrjEditable):
    log.info('Can\'t find synthesis.prj')
    log.info('Search paths: ' + pathSynthesisPrj + ';' + pathSynthesisPrjEditable)
    return True
  
  pathEdif = pathCur + '/../synthesis/' + iTopModule + '.edf'
  if iTopModule and not os.path.exists(pathEdif):
    log.info("can't find " + pathEdif)
    return True
  
  if not filecmp.cmp(pathSynthesisPrj, pathSynthesisPrjEditable):
    log.info('mismatch /synthesis/synthesis.prj and /script/synthesis.prj')
    return True
  log.info('No need to resynthesis')  
  return False



def getSrcFromFileSys():
  '''
  Returns edf, ndf, ucf files by filter
  '''
  log.debug('def getSrcFromFileSys IN')
  scriptContentSyn = getContentSyn()
  topModule = getParam('set_option -top_module', scriptContentSyn)
  topModuleName = topModule[1].strip('"')
  topRes = [topModuleName+'\.edf', topModuleName+'\.ucf']
  IMPL_EXT = ['ucf', 'edf', 'ndf', 'ngc']
  ext = []
  ext = build.getSrcExtensions(iTag='implement_ext')
  if not ext:
    log.warning("Can't get extensions from build.xml. Using default="+str(IMPL_EXT))
    ext = IMPL_EXT
  ext = ['/src/.*?'+i+'$' for i in ext]
  only = ext + topRes
  src = structure.search(iPath = '..', iOnly = only)
  src = [(os.path.abspath(i)).replace('\\', '/') for i in src]
  log.debug('def getSrcFromFileSys OUT src='+str(src))
  return src



def getSrcFromScript(iScriptContent):
  '''
  Returns scr files as list of strings.
  String contains comments and "xfile add".
  '''
  log.debug('def getSrcFromScript=> iScriptContent=\n'+iScriptContent)
  xfile = re.findall('.*?xfile\s+add\s+.*', iScriptContent)
  return xfile


def genScript(iTopModule = ''):
  log.debug('def genScript=> iTopModule='+iTopModule)
  pathCur = os.getcwd().replace('\\', '/')
  
  if needResynthesis(iTopModule):
    log.info('Resynthesis...')
    synthesis.run('synplify_batch', iTopModule = iTopModule)

  scriptContentSyn = getContentSyn()
  scriptContentImpl = getContentImpl()
  
  global gSynToImpl
  scriptContentImplNew = refreshParams(scriptContentSyn,
                                      scriptContentImpl,
                                      gSynToImpl)
  
  f = open(pathCur + '/implement.tcl', 'w')
  f.write(scriptContentImplNew)
  f.close()


def run(iTopModule = ''):  
  log.debug('def run=> iTopModule='+iTopModule)  
  try:
    if os.path.exists('../implement'):
      shutil.rmtree('../implement')
  except OSError:
    log.warning('Can\'t delete folder ../implement')
  
  genScript(iTopModule = iTopModule)
  
  ise_batch = toolchain.getPath('ise_batch')
  subprocess.call([ise_batch, os.getcwd() + '/implement.tcl'])

  log.info('Implementation done')
