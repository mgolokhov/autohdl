from xml.dom import minidom
import os

from hdlLogger import *

def genPredef(iPath, iDsnName):
  '''
  Generates predefined build.xml
  '''
  log.debug('def genPredef IN iPath='+iPath+' iDsnName='+iDsnName)
  buildContent = '''\
  <!--default build-->
  <wsp>
    <dsn id="{DESIGN_NAME}">
      <dep>{DEP}</dep>
      <synthesis_ext>{SYN_EXT}</synthesis_ext>
      <implement_ext>{IMPL_EXT}</implement_ext>
    </dsn>
  </wsp>
  '''.format(DESIGN_NAME=iDsnName,
             DEP='',
             SYN_EXT = 'v; vm; vhd; vhdl',
             IMPL_EXT = 'ucf; edf; ndf; ngc'
             )
  pathBuild = iPath+'/build.xml'
  if not os.path.exists(pathBuild):
    f = open(pathBuild, 'w')
    f.write(buildContent)
    f.close()
  log.debug('def genParedef OUT')

def getDeps(iDsnName = '', iBuildFile = 'build.xml'):
  '''
  Returns: dictionary key=dsnName, value=list of dependences as full path;
  '''
  log.debug('def getDeps IN iDsnName='+iDsnName+' iBuildFile='+iBuildFile)
  if not os.path.exists(iBuildFile):
    log.warning("Can't find file: " + iBuildFile)
    return
  
  pathBuildFile = os.path.abspath(iBuildFile).replace('\\','/')
  pathDsn = '/'.join(pathBuildFile.split('/')[:-3])

  dom = minidom.parse(pathBuildFile)
  dsnNodes = dom.firstChild.childNodes
  dependences = {}
  for node in  dsnNodes:
    if node.attributes:
      dsnName = node.attributes['id'].value
      dep = node.getElementsByTagName('dep')
      dsnDep = []
      for k in dep:
        pathDep = (k.firstChild.data).strip()
        pathDepAbs = '%s/%s' % (pathDsn, pathDep)
        pathDepAbs = os.path.abspath(pathDepAbs).replace('\\','/')
        if not os.path.exists(pathDepAbs):
          log.warning('Wrong dep path: '+pathDepAbs+'; in file: '+iBuildFile)
          continue 
        dsnDep.append(pathDepAbs)
      dependences[dsnName] = dsnDep
      if iDsnName == dsnName:
        break
  log.debug('def getDeps OUT dependences='+str(dependences))
  return dependences


def getSrcExtensions(iTag, iBuildFile='../resource/build.xml'):
  '''
  Input: tag (e.g. synthesis_ext, implement_ext), path to buildXml;
  Output: list of extensions (e.g. [.v, .vhdl, .vm])
  Tag example: <synthesis_ext>v;vhdl;vm</synthesis_ext>
  '''
  log.debug('def getSrc IN iTag='+iTag+'; iBuildFile='+iBuildFile)
  iBuildFile = os.path.abspath(iBuildFile)
  if not os.path.exists(iBuildFile):
    log.warning("Can't find file: "+iBuildFile)
    return  
  dom = minidom.parse(iBuildFile)
  extensions = dom.getElementsByTagName(iTag)
  if not extensions:
    log.warning("Can't find tag="+iTag+'; in file='+iBuildFile)
    return
  extensions = extensions[0].childNodes[0].toxml().strip().strip(';')
  extensions = [i.strip() for i in extensions.split(';')]
  return extensions
  
