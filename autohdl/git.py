import argparse
import os
import shutil
import subprocess
import urlparse

from pyparsing import makeHTMLTags, SkipTo

from autohdl import toolchain
import webdav
from autohdl.hdlLogger import logging
from autohdl.hdlGlobals import implementPath
import autohdl.doc as doc
from autohdl.hdlGlobals import autohdlRoot


def initialize(path = '.'):
  if os.path.exists(path+'/.git'):
    print 'Already initialized'
    return
  gitPath = toolchain.Tool().get('git_batch')
  if gitPath:
    path = os.path.abspath(path)
    subprocess.call('{} init {}'.format(gitPath, path))
    gitignore = path+'/.gitignore'
    if not os.path.exists(gitignore):
      with open(gitignore, 'w') as f:
        f.write('{}/*\n'.format(autohdlRoot))
    pathWas = os.getcwd()
    os.chdir(path)
    subprocess.call('{} add {}'.format(gitPath, path))
    subprocess.call('{} commit -m "initial commit"'.format(gitPath))
    os.chdir(pathWas)


def upload(path = '.', addr = 'http://cs.scircus.ru/git/hdl'):
  gitPath = toolchain.Tool().get('git_batch')
  if gitPath:
    initialize(path)
    path = os.path.abspath(path)
    _, name = os.path.split(path)
    os.chdir(path+'/.git')
    subprocess.call(gitPath+' update-server-info')
    os.chdir('..')
    #_netrc
    res = urlparse.urlparse(addr)
    webdav.upload(src=path+'/.git',
                  dst='{0}/{1}.git'.format(res.path,name),
                  host=res.hostname)
    subprocess.call('{0} remote add webdav {1}/{2}.git'.format(gitPath, addr, name))

def pull(config):
  gitPath = toolchain.Tool().get('git_batch')
  if gitPath:
    cwdWas = os.getcwd()
    repos = []
    for root, dirs, files in os.walk('.'):
      if '.git' in dirs:
        dirs[:] = []
        repos.append(root)
    for repo in repos:
#      repo /= os.path.basename(os.path.abspath(r))
      print repo, ' ',
      os.chdir(repo)
      subprocess.call('"{}" pull webdav'.format(gitPath))
      os.chdir(cwdWas)


def getRepos(client, path):
  logging.info('Scanning repos')
  response = client.propfind('/{}/'.format(path),
                                           depth=1)
  anchorStart, anchorEnd = makeHTMLTags('D:href')
  anchor = anchorStart + SkipTo(anchorEnd).setResultsName('body') + anchorEnd
  return [tokens.body for tokens in anchor.searchString(response.content) if '.git' in tokens.body]


def clone(config):
  gitPath = toolchain.Tool().get('git_batch')
  if gitPath:
    client = webdav.connect(config['host'])
    repos = getRepos(client, config['webdavSrcPath'])
    for repo in repos:
      subprocess.call('{} clone http://{}/{} -o webdav'.format(gitPath, config['host'], repo))

    repos = getRepos(client, config['webdavSrcPath']+'/cores/')
    if not os.path.exists('cores'):
      os.mkdir('cores')
    os.chdir('cores')
    for repo in repos:
      subprocess.call('{} clone http://{}/{} -o webdav'.format(gitPath, config['host'], repo))
    os.chdir('..')

def backupFirmware(config):
  for i in ['.bit', '.mcs']:
    firmware = os.path.join(implementPath, config.get('top')+i)
    print firmware
    if os.path.exists(firmware):
      shutil.copy(firmware, os.path.join('..', 'resource', config.get('top')+i))

def updateGitignore():
  if os.path.exists('../.gitignore'):
    with open('../.gitignore', 'r') as f:
      c = f.read()
    with open('../.gitignore', 'a') as f:
      if autohdlRoot not in c:
        f.write('{}/*\n'.format(autohdlRoot))


def synchWithBuild(config):
  backupFirmware(config)
  gitPath = toolchain.Tool().get('git_batch')
  res = subprocess.Popen('{} status'.format(gitPath),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
  if 'working directory clean' in res.stdout.read():
    return
  updateGitignore()
  res = subprocess.Popen('{} branch'.format(gitPath),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)

  if ' develop\n' in res.stdout.read():
    subprocess.call('{} checkout develop'.format(gitPath))
  else:
    subprocess.call('{} checkout -b develop'.format(gitPath))
  subprocess.call('{} add ../.'.format(gitPath))
  #TODO: unicode
  subprocess.call('{} commit -m "{}"'.format(gitPath, config.get('gitMessage')))


def synchWithBuild2(config):
  """integration with bitbucket"""
  backupFirmware(config)
  cwd_was = os.getcwd()
  git_root_dir = subprocess.check_output('git rev-parse --show-toplevel')
  os.chdir(git_root_dir)
  try:
    print subprocess.check_output('git add -A')
    print subprocess.check_output('git commit')
    print subprocess.check_output('git push all')
  except:
    os.chdir(cwd_was)
    raise


def getGitRoot(path):
  pathWas = os.path.abspath(path)
  path = pathWas
  while os.path.sep in path:
    if os.path.exists(path+'/.git'):
      logging.info('Path changed to '+path)
      return path
    path = os.path.dirname(path).rstrip(os.path.sep)
  logging.warning('Cant find git repo, using current directory')
  return pathWas


def commands():
  parser = argparse.ArgumentParser(add_help=False)
  parser.add_argument('-git',
                      choices=['upload', 'cmd', 'pull', 'clone', 'doc'],
                      help='creation/synchronization with webdav repo'
                      )
  return parser


def handle(config):
  if config['git'] == 'upload':
    pathWas = os.getcwd()
    os.chdir(getGitRoot(pathWas))
    webdavSrcPath = config.get('webdavSrcPath')
    host = config.get('host')
    core = config.get('core')
    addr = 'http://{0}/{1}/{2}'.format(host, webdavSrcPath, core if core else '')
    upload('.', addr)
  elif config['git'] == 'cmd':
    gitPath = toolchain.Tool().get('git_sh')
    if gitPath:
      pathWas = os.getcwd()
      os.chdir(getGitRoot(pathWas))
      subprocess.call('{} --login -i'.format(gitPath))
#      os.chdir(pathWas)
  # pull & clone don't depend on root path
  elif config['git'] == 'pull':
    pull(config)
  elif  config['git'] == 'clone':
    clone(config)
  elif config['git'] == 'doc':
    doc.handler('git')
