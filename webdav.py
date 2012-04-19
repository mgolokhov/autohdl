import base64
import os
import socket
import sys
import getpass

from autohdl import build
import autohdl.lib.tinydav as tinydav
from autohdl.lib.pyparsing import makeHTMLTags, SkipTo
from autohdl.lib.tinydav.exception import HTTPUserError
import autohdl.lib.yaml as yaml
from autohdl.hdlLogger import log_call, logging

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


def checkAuth(host, iUsername, iPassword):
  client = tinydav.HTTPClient(host)
  client.setbasicauth(iUsername, iPassword)
  try:
    print client.head('/test')
  except HTTPUserError as e:
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


def dump_netrc(host, username, password):
  path = os.environ['USERPROFILE']+'/_netrc'
  data = 'machine {0}\nlogin {1}\npassword {2}\n'.format(host, username, password)
  with open(path, 'w') as f:
    f.write(data)


def authenticate(host = 'cs.scircus.ru'):
  print 'Authentication',
  path = sys.prefix + '/Lib/site-packages/autohdl_cfg/open_sesame'
  username, password = loadAuth(path)
  state = 'check'
  while True:
    if state == 'check':
      if checkAuth(host, username, password):
        state = 'dump'
      else:
        state = 'ask'
    elif state == 'ask':
      username, password = askAuth()
      state = 'check'
    elif state == 'dump':
      #TODO: constant rewriting
      dumpAuth(path, username, password)
      dump_netrc(host, username, password)
      return username, password


def exists(path, client):
  try:
    client.get(path)
  except HTTPUserError:
    sys.exit()


def getBuildVer(client, folder, root_build):
  """
  Get build version
  """
  response = client.propfind('/{}/'.format(folder), depth=1)
  anchorStart, anchorEnd = makeHTMLTags('D:href')
  anchor = anchorStart + SkipTo(anchorEnd).setResultsName('body') + anchorEnd
  fwList = {os.path.basename(tokens.body) for tokens in anchor.searchString(response.content)}
  try:
    # get rid of extensions
    fwList = [os.path.splitext(i)[0] for i in fwList if root_build in i]
    allBuilds = []
    for i in fwList:
      try:
        # ripping only build versions
        allBuilds.append(int(i.split(root_build)[1]))
      except Exception:
        continue
    buildNum = max(allBuilds)
  except Exception as e:
    buildNum = 0
  return buildNum


def formBaseInfo(conf):
  b = conf or build.load()
  comment = raw_input('Add some comment: ')
#  conf['gitMessage'] += comment
  content = 'encoding: utf-8\ncomment: {}\ndevice: {}\nPROM size: {} kilobytes\nspi: {}'.format(
                            comment, b.get('device'), b.get('size'), b.get('spi'))
  print content
  conf['gitMessage'] += comment.decode(sys.stdin.encoding or 'utf-8').encode('utf-8')
  return content.decode(sys.stdin.encoding or 'utf-8').encode('utf-8')


def upload_fw(file, host = 'cs.scircus.ru', path = '/test/distout/rtl', _cache = {}, conf = ''):
  # dsn_name/implement/file
  client = connect(host)
  dsn_name = os.path.abspath(file).replace('\\', '/').split('/')[-3]
  root, ext = os.path.splitext(os.path.basename(file))
  key = dsn_name+root
  name = _cache.get(key)
#  content = getContent(file)
  try:
    with open(file, 'rb') as f:
      content = f.read()
  except IOError:
    print 'Cant open file ' + os.path.abspath(file)
    return
  if not name:
    folder = path+'/'+dsn_name
    print 'Uploading folder: ', folder,
    print client.mkcol(folder)
    buildNum = getBuildVer(client, folder, root+'_build_')+1
    conf['gitMessage'] = 'build_{} '.format(buildNum)
    name = '{path}/{dsn}/{dsn}_{root}_build_{num}'.format(
        path=path, dsn=dsn_name, root=root, num=buildNum)

    dst = name + '_info'
    info = formBaseInfo(conf)
    print 'Uploading info: ', dst,
    print client.put(dst, info)

    _cache.update({key:name})

  dst = name + ext
  print 'Uploading file: ', dst,
  print client.put(dst, content)



def getContent(iFile):
  try:
    with open(iFile, "rb") as f:
      data = f.read()
  except IOError as e:
    print e
    sys.exit()
  return data


def connect(host='cs.scircus.ru'):
  try:
    username, password = authenticate(host)
    client = tinydav.WebDAVClient(host)
    client.setbasicauth(username, password)
    return client
  except socket.gaierror as e:
    print e
    print 'Cant connect to server'
    sys.exit()

@log_call
def upload(src, dst, host = 'cs.scircus.ru'):
  #TODO: atomic uploading
  client = connect(host)
  try:
    d = dst if dst[-1] != '/' else dst[:-1]
    client.get(os.path.dirname(d))
  except HTTPUserError as e:
    print 'Wrong destination:', dst, e
    sys.exit()

  try:
    if 'HTTP/1.1 200 OK' in client.propfind(dst+'//').content:
      print 'Already exists: ', dst
      sys.exit()
  except HTTPUserError:
    pass

  if os.path.isfile(src):
    content = getContent(src)
    print 'Uploading file: ', dst,
    print client.put(dst, content)
  else:
    path_was = os.getcwd()
    print dst, client.mkcol(dst)
    try:
      os.chdir(src)
      for root, dirs, files in os.walk('.'):
        for d in dirs:
          ad = os.path.join(root,d).replace('\\', '/')
          web_dst = '{0}{1}'.format(dst,ad.replace('./', '/'))
          print web_dst,
          print client.mkcol(web_dst)
        for f in files:
          af = os.path.join(root,f).replace('\\','/')
          web_dst = '{0}{1}'.format(dst,af.replace('./', '/'))
          print web_dst,
          content = open(af).read()

          headers = None if content else {'Content-Length': 0}
          print client.put(web_dst,
                           content,
                           headers = headers)
    finally:
      os.chdir(path_was)




if __name__ == '__main__':
  print authenticate()