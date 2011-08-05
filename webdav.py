import base64
import os
import sys
import getpass
import lib.tinydav as tinydav
from lib.pyparsing import makeHTMLTags, SkipTo

import lib.yaml as yaml

from hdlLogger import log_call, logging
log = logging.getLogger(__name__)

def loadAuth(iPath):
  username, password = '', ''
  try:
    with open(iPath) as f:
      content = yaml.load(f)
      username = base64.decodestring(content[base64.encodestring('username')])
      password = base64.decodestring(content[base64.encodestring('password')])
  except Exception as e:
    # logging e
    logging.debug(e)
  return username, password


def checkAuth(iUsername, iPassword):
  client = tinydav.HTTPClient('cs.scircus.ru')
  client.setbasicauth(iUsername, iPassword)
  try:
    print client.head('/test/')
  except tinydav.exception.HTTPUserError as e:
    #logging
    print e
    logging.debug(e)
    return False
  return True


def dumpAuth(iPath, iUsername, iPassword):
  contentYaml = {base64.encodestring('username'): base64.encodestring(iUsername),
                 base64.encodestring('password'): base64.encodestring(iPassword)}
  try:
    with open(iPath, 'wb') as f:
      yaml.dump(contentYaml, f, default_flow_style = False)
  except IOError as e:
    print e


def askAuth():
  quit = raw_input('To cancel hit Q, Enter to continue: ')
  if quit.lower() == 'q':
    print 'Exit...'
    sys.exit(0)
  username = raw_input('user: ')
  password = getpass.getpass('password: ')
  return username, password


def authenticate():
  print 'Authentication'
  path = sys.prefix + '/Lib/site-packages/autohdl_cfg/open_sesame'
  username, password = loadAuth(path)
  state = 'check'
  while True:
    if state == 'check':
      if checkAuth(username, password):
        state = 'dump'
      else:
        state = 'ask'
    elif state == 'ask':
      username, password = askAuth()
      state = 'check'
    elif state == 'dump':
      dumpAuth(path, username, password)
      return username, password


def formBuildName(iUsername, iPassword, iFile, _cache = []):
  dsnName = os.path.abspath(iFile).replace('\\', '/').split('/')[-3]
  root, ext = os.path.splitext(os.path.basename(iFile))
  root_build = root + '_build_'
  if _cache:
    return '{dsn}_{root_build}{num}{ext}'.format(dsn=dsnName,
                                                root_build=root_build,
                                                num=_cache[0],
                                                ext=ext)

  client = tinydav.WebDAVClient('cs.scircus.ru')
  client.setbasicauth(iUsername, iPassword)
  response = client.propfind('/test/distout/rtl/{dsnName}/'.format(dsnName=dsnName),
                             depth=1,
                             properties=['href'])
  anchorStart, anchorEnd = makeHTMLTags('D:href')
  anchor = anchorStart + SkipTo(anchorEnd).setResultsName('body') + anchorEnd
  fwList = {os.path.basename(tokens.body) for tokens in anchor.searchString(response.content)}
  try:
    fwList = [os.path.splitext(i)[0] for i in fwList if root_build in i]
    allBuilds = []
    for i in fwList:
      try:
        allBuilds.append(int(i.split(root_build)[1]))
      except Exception:
        continue
    incBuildNum = max(allBuilds) + 1
  except Exception as e:
    incBuildNum = 0
  _cache.append(incBuildNum)
  name = '{dsn}_{root_build}{num}{ext}'.format(dsn=dsnName,
                                               root_build=root_build,
                                               num=incBuildNum,
                                               ext=ext)
  return name


def getContent(iFile):
  try:
    with open(iFile, "rb") as f:
      data = f.read()
  except IOError as e:
    print e
    sys.exit()
  return data


@log_call
def upload(iFile):
  content = getContent(iFile)
  username, password = authenticate()

  client = tinydav.WebDAVClient('cs.scircus.ru')
  client.setbasicauth(username, password)

  dsnName = os.path.abspath(iFile).replace('\\', '/').split('/')[-3]
  print client.mkcol('/test/distout/rtl/' + dsnName)

  name = formBuildName(username, password, iFile)
  print 'Uploading file: ', name
  response = client.put('/test/distout/rtl/{dsnName}/{name}'.format(dsnName=dsnName, name=name),
                        content,
                        "application/binary")
  print response.statusline





if __name__ == '__main__':
  upload('webdav.py')
