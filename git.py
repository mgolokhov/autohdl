import os
import subprocess
import urlparse

from autohdl.lib.pyparsing import makeHTMLTags, SkipTo
from autohdl import toolchain
from autohdl import webdav
from autohdl.hdlLogger import logging


def initialize(path = '.'):
  gitPath = toolchain.Tool('git_batch').result
  if gitPath:
    path = os.path.abspath(path)
    subprocess.call('{} init {}'.format(gitPath, path))
    gitignore = path+'/.gitignore'
    if not os.path.exists(gitignore):
      with open(gitignore, 'w') as f:
        f.write('aldec/*\nimplement/*\nsynthesis/*\nresource/parsed/*\n')


def upload(path = '.', addr = 'http://cs.scircus.ru/git/hdl'):
  gitPath = toolchain.Tool('git_batch').result
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
  gitPath = toolchain.Tool('git_batch').result
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
  gitPath = toolchain.Tool('git_batch').result
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

      
def handle(arg, config):
  if arg == 'upload':
    webdavSrcPath = config.get('webdavSrcPath')
    host = config.get('host')
    core = config.get('core')
    if host and webdavSrcPath:
      addr = 'http://{0}/{1}/{2}'.format(host, webdavSrcPath, core if core else '')
      upload('..', addr)
    else:
      upload('..')
  elif arg == 'cmd':
    gitPath = toolchain.Tool('git_sh').result
    if gitPath:
      subprocess.call('{} --login -i'.format(gitPath))
  elif arg == 'pull':
    pull(config)
  elif  arg == 'clone':
    clone(config)
  elif arg == 'help':
    subprocess.Popen(os.path.dirname(__file__)+'/doc/git.html', shell = True)