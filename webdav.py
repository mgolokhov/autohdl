import base64
import os
import socket
import subprocess
import sys
import getpass
import urlparse
import lib.tinydav as tinydav
from lib.pyparsing import makeHTMLTags, SkipTo
from lib.tinydav.exception import HTTPUserError

import lib.yaml as yaml

from hdlLogger import log_call, logging
import toolchain

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


def authenticate(host):
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


def upload_fw(file, host = 'cs.scircus.ru', path = '/test/distout/rtl', _cache = []):
  # dsn_name/implement/file
  dsn_name = os.path.abspath(file).replace('\\', '/').split('/')[-3]
  client = connect(host)
  print 'Uploading folder: ', path+'/'+dsn_name,
  print client.mkcol(path+'/'+dsn_name)
  root, ext = os.path.splitext(os.path.basename(file))
  root_build = root + '_build_'
  content = getContent(file)
  if _cache:
    dst = path+'/'+dsn_name+'/'+'{dsn}_{root_build}{num}{ext}'.format(dsn=dsn_name,
                                                                      root_build=root_build,
                                                                      num=_cache[0],
                                                                      ext=ext)
    print 'Uploading file: ', dst,
    print client.put(dst, content)
    return
  response = client.propfind('/{root}/{dsn_name}/'.format(root = path,
                                                          dsn_name = dsn_name),
                             depth=1)
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
  name = '{dsn}_{root_build}{num}{ext}'.format(dsn=dsn_name,
                                               root_build=root_build,
                                               num=incBuildNum,
                                               ext=ext)
  dst = path+'/'+dsn_name+'/'+name
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

def git_init(src = '.', addr = 'http://cs.scircus.ru/git/hdl'):
  src = os.path.abspath(src)
  print src
  if os.path.exists(src+'/.git'):
    print 'Local repo already exists: ', src
    return
  path_git = toolchain.Tool('git_batch').result
  dirname, name = os.path.split(src)
  subprocess.call('{0} init {1}'.format(path_git,src))
  os.chdir(src+'/.git')
  subprocess.call(path_git+' update-server-info')
  os.chdir('..')
  #_netrc
  res = urlparse.urlparse(addr)
  upload(src=src+'/.git', dst='{0}/{1}.git'.format(res.path,name), host=res.hostname)
  subprocess.call('{0} remote add webdav {1}/{2}.git'.format(path_git, addr, name))
  


if __name__ == '__main__':
  print authenticate('cs.scircus.ru')