import argparse
import os
import subprocess
import urlparse

from autohdl.lib.pyparsing import makeHTMLTags, SkipTo
from autohdl import toolchain
from autohdl import webdav
from autohdl.hdlLogger import logging
import autohdl.doc as doc


def initialize(path = '.'):
  if os.path.exists(path+'/.git'):
    print 'Already initialized'
    return
  gitPath = toolchain.Tool().get('git_batch')
  if gitPath:
    path = os.path.abspath(path)
    print subprocess.check_output('{} init {}'.format(gitPath, path))
    gitignore = path+'/.gitignore'
    if not os.path.exists(gitignore):
      with open(gitignore, 'w') as f:
        f.write('aldec/*\nimplement/*\nsynthesis/*\nresource/parsed/*\n')
    pathWas = os.getcwd()
    os.chdir(path)
    print subprocess.check_output('{} add {}'.format(gitPath, path))
    print subprocess.check_output('{} commit -m "initial commit"'.format(gitPath))
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


def synchWithBuild(config):
  gitPath = toolchain.Tool().get('git_batch')
  res = subprocess.check_output('{} status'.format(gitPath))
  if 'working directory clean' in res:
    return
  res = subprocess.check_output('{} branch'.format(gitPath))
  if ' develop\n' in res:
    print subprocess.check_output('{} checkout develop'.format(gitPath))
  else:
    print subprocess.check_output('{} checkout -b develop'.format(gitPath))
  print subprocess.check_output('{} add ../.'.format(gitPath))
  #TODO: unicode
  print subprocess.check_output('{} commit -m "{}"'.format(gitPath, config.get('gitMessage')))


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
