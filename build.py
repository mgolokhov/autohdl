from xml.dom import minidom
import os

from hdlLogger import *

def genPredef(iPath, iDsnName):
  '''
  Generates predefined build.xml
  '''
  log.debug('def genPredef<= iPath='+iPath+' iDsnName='+iDsnName)
  buildContent = '''\
  <!--default build-->
  <wsp>
    <dsn id="{DESIGN_NAME}">
      <dep>{DEPENDENCES}</dep> 
    </dsn>
  </wsp>
  '''.format(DESIGN_NAME=iDsnName, DEPENDENCES='')
  pathBuild = iPath+'/build.xml'
  if not os.path.exists(pathBuild):
    f = open(pathBuild, 'w')
    f.write(buildContent)
    f.close()
  log.debug('def genParedef=>')

def getDeps(iDsnName = '', iBuildFile = 'build.xml'):
  '''
  Returns: dictionary key=dsnName, value=list of dependences as full path;
  '''
  log.debug('def getDeps<= iDsnName='+iDsnName+' iBuildFile='+iBuildFile)
  if not os.path.exists(iBuildFile):
    log.warning('Can\'t find file: ' + iBuildFile)
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
  log.debug('def getDeps=> dependences='+str(dependences))
  return dependences




