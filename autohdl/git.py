import argparse
import os
import re
import subprocess
import urllib.parse
import sys

from pyparsing import makeHTMLTags, SkipTo
from autohdl import toolchain
import autohdl.webdav as webdav
from autohdl.hdlLogger import logging
import autohdl.doc as doc
from autohdl.hdlGlobals import autohdlRoot


def initialize(path='.'):
    if os.path.exists(path + '/.git'):
        print('Already initialized')
        return
    gitPath = toolchain.Tool().get('git_batch')
    if gitPath:
        path = os.path.abspath(path)
        subprocess.call('{} init {}'.format(gitPath, path))
        gitignore = path + '/.gitignore'
        if not os.path.exists(gitignore):
            with open(gitignore, 'w') as f:
                f.write('{}/*\n'.format(autohdlRoot))
        pathWas = os.getcwd()
        os.chdir(path)
        subprocess.call('{} add {}'.format(gitPath, path))
        subprocess.call('{} commit -m "initial commit"'.format(gitPath))
        os.chdir(pathWas)


def upload(path='.', addr='http://cs.scircus.ru/git/hdl'):
    gitPath = toolchain.Tool().get('git_batch')
    if gitPath:
        initialize(path)
        path = os.path.abspath(path)
        _, name = os.path.split(path)
        os.chdir(path + '/.git')
        subprocess.call(gitPath + ' update-server-info')
        os.chdir('..')
        #_netrc
        res = urllib.parse.urlparse(addr)
        webdav.upload(src=path + '/.git',
                      dst='{0}/{1}.git'.format(res.path, name),
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
            print(repo, ' ', end=' ')
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
        client = webdav.connect(config['hdlManager']['host'])
        repos = getRepos(client, config['hdlManager']['webdavSrcPath'])
        for repo in repos:
            subprocess.call('{} clone http://{}/{} -o webdav'.format(gitPath, config['hdlManager']['host'], repo))

        repos = getRepos(client, config['hdlManager']['webdavSrcPath'] + '/cores/')
        if not os.path.exists('cores'):
            os.mkdir('cores')
        os.chdir('cores')
        for repo in repos:
            subprocess.call('{} clone http://{}/{} -o webdav'.format(gitPath, config['hdlManager']['host'], repo))
        os.chdir('..')


def get_last_build_num(top):
    p = subprocess.Popen('git log -1 --grep="{top}_build_" --all'.format(top=top),
                         stderr=subprocess.PIPE,
                         stdout=subprocess.PIPE)
    out, err = p.communicate()
    res = re.search(r'\w*_build_(\d+):', out + err)
    num = int(res.group(1)) if res else 0
    return num


def updateGitignore():
    if os.path.exists('../.gitignore'):
        with open('../.gitignore', 'r') as f:
            c = f.read()
        with open('../.gitignore', 'a') as f:
            if autohdlRoot not in c:
                f.write('{}/*\n'.format(autohdlRoot))


def synchWithBuild(config):
#  backupFirmware(config)
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


def _popen(prog, shell=True):
    p = subprocess.Popen(prog,
                         shell=shell,
                         stderr=subprocess.PIPE,
                         stdout=subprocess.PIPE
    )
    out, err = p.communicate()
    return p, out, err


def valid_firmware(config):
    ver = get_last_build_num(config['hdlManager']['top'])
    folder = os.path.abspath(os.path.join(config['hdlManager']['dsn_root'],
                                          'resource'))
    for fw in os.listdir(folder):
        name, e = os.path.splitext(fw)
        for valid_ext in ['.bit', '.mcs']:
            if config['hdlManager']['top'] in name and valid_ext == e and ver < int(name.split('_build_')[1]):
                config['firmware_{ext}'.format(ext=valid_ext[1:])] = os.path.join(folder, fw)
    if config.get('firmware_bit') or config.get('firmware_mcs'):
        return True
    else:
        print('Old version of firmware, nothing to upload')
        return False


def push_firmware(config):
    """integration with bitbucket"""
    # if not valid_firmware(config):
    #     return
    cwd_was = os.getcwd()
    git_root_dir = subprocess.check_output('git rev-parse --show-toplevel')
    git_root_dir = git_root_dir.strip().strip('\n')
    os.chdir(git_root_dir)
    try:
        p, out, err = _popen('git status -s')
        print(out + err)
        mes = config['publisher']['message']
        mes = '{comment}; \n' \
              'technology: {technology}; part: {part}; package: {package}; ' \
              'PROM size: {size} kilobytes; '.format(comment=mes,
                                                     technology=config['hdlManager'].get('technology'),
                                                     part=config['hdlManager'].get('part'),
                                                     package=config['hdlManager'].get('package'),
                                                     size=config['hdlManager'].get('size'),
        )
        config['hdlManager']['git_mes'] = mes
        p, out, err = _popen('git add -A')
        print(out + err)
        mes = mes.decode(sys.stdin.encoding).encode('cp1251')
        p, out, err = _popen('git commit -m"_build_: {mes}"'.format(mes=mes))
        print(out + err)
        p, out, err = _popen('git push bitbucket --all', shell=False)
        print(out + err)
    finally:
        os.chdir(cwd_was)


def getGitRoot(path):
    pathWas = os.path.abspath(path)
    path = pathWas
    while os.path.sep in path:
        if os.path.exists(path + '/.git'):
            logging.info('Path changed to ' + path)
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
    elif config['git'] == 'clone':
        clone(config)
    elif config['git'] == 'doc':
        doc.handler('git')
