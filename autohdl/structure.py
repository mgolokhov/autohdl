import re
import os
import shutil
from collections import namedtuple

from autohdl import instance
from autohdl import hdlGlobals
from autohdl import progressBar

from autohdl.hdlLogger import log_call, logging

log = logging.getLogger(__name__)


def generate(path=''):
    """
    Could be
    empty
    simple name
    path
    """
    root = os.path.abspath(path)
    if not os.path.exists(root):
        os.makedirs(root)
    log.info('Design root: ' + root)
    for i in hdlGlobals.predefDirs:
        path = os.path.join(root, i)
        if not os.path.exists(path):
            os.mkdir(path)

    pathData = os.path.join(os.path.dirname(__file__), 'data')
    autohdl_cfg = os.path.join(os.path.expanduser('~'), 'autohdl')
    Copy = namedtuple('Copy', ['src', 'dst'])
    listToCopy = (
        Copy(os.path.join(autohdl_cfg, 'build.yaml'), os.path.join(root, 'resource', 'build.yaml')),
        Copy(os.path.join(pathData, 'run_avhdl.bat'), os.path.join(root, 'script', 'run_avhdl.bat')),
        Copy(os.path.join(pathData, 'kungfu.py'), os.path.join(root, 'script', 'kungfu.py'))
    )
    for i in listToCopy:
        if not os.path.exists(i.dst):
            shutil.copy(i.src, i.dst)
    return get(root)


def get(path='', ignore=('.git', '.svn')):
    root = os.path.abspath(path)
    return tree(directory=root, ignore=ignore)


def tree(directory, padding=' ', _res=[], ignore=[]):
    _res.append(padding[:-1] + '+-' + os.path.basename(os.path.abspath(directory)) + os.path.sep)
    padding += ' '
    files = os.listdir(directory)
    count = 0
    for f in files:
        if f in ignore:
            continue
        count += 1
        _res.append(padding + '|')
        path = directory + os.path.sep + f
        if os.path.isdir(path):
            if count == len(files):
                tree(directory=path, padding=padding + ' ')
            else:
                tree(directory=path, padding=padding + '|')
        else:
            _res.append(padding + '+-' + f)
    return '\n'.join(_res)


def pathOk(path, ignore, only):
    if ignore:
        for ignoreItem in ignore:
            if re.search(ignoreItem, path):
                return False
    if only:
        for onlyItem in only:
            if re.search(onlyItem, path):
                return True
    else:
        return True


def _convertToSet(arg):
    arg = arg or set()
    if type(arg) is str:
        arg = [arg]
    return set(arg)


@log_call
def search(directory='.',
           ignoreDir=None, ignoreExt=None, onlyExt=None):
    """
      Recursively search files by pattern.
      Input: directory - start point to search,
             ignore and only - filter patterns for directory and files (should be lists)
      Returns list of files.
    """
    ignoreDir = _convertToSet(ignoreDir)
    ignoreExt = _convertToSet(ignoreExt)
    onlyExt = _convertToSet(onlyExt)

    resFiles = []
    for root, dirs, files in os.walk(os.path.abspath(directory)):
        for i in set(dirs) & ignoreDir:
            log.debug('ignore directory: ' + i)
            dirs.remove(i)
        for f in files[:]:
            log.debug('file: ' + f)
            ext = os.path.splitext(f)[1]
            if ext in ignoreExt:
                files.remove(f)
                log.debug('ignore file (ignore list) ' + f)
            elif onlyExt and (ext not in onlyExt):
                files.remove(f)
                log.debug('ignore file (only list) ' + f)
            else:
                log.debug('add file ' + f)
                resFiles.append(os.path.join(root, f))
    return resFiles


########################################################################
@log_call
def setMainSrc(config):
    config.setdefault('structure', dict())
    config['structure']['mainSrc'] = search('../src',
                                            onlyExt=hdlGlobals.hdlFileExt,
                                            ignoreDir=hdlGlobals.ignoreRepoDir)
    config['structure']['mainSrcParsed'] = instance.get_instances(config['structure']['mainSrc'])


def setNetlists(config):
    config['structure']['netlists'] = set()
    for i in config['structure']['mainSrc'] + config['structure']['depSrc']:
        as_netlist = os.path.splitext(i)[0] + '.ngc'
        if os.path.exists(as_netlist):
            config['structure']['netlists'].add(as_netlist)


def setSrc(config):
    config.setdefault('structure', dict())
    log.info('Analyzing dependences...')
    progressBar.run()
    setMainSrc(config)
    setDepSrc(config)
    setNetlists(config)
    progressBar.stop()


@log_call
def setDepSrc(config):
    config.setdefault('structure', dict())
    parsed = config['structure']['mainSrcParsed']
    del config['structure']['mainSrcParsed']
    while True:
        new = instance.analyze(parsed, config)
        if new:
            parsed.update(new)
        else:
            break

    config['structure']['parsed'] = parsed
    allSrcFiles = {os.path.abspath(val['path']) for val in parsed.values()}
    config['structure']['depSrc'] = list(allSrcFiles - set(config['structure']['mainSrc']))


if __name__ == '__main__':
    res = []
    res += [search(directory=i) for i in ['verilog', 'programmator']]
    #  print '\n'.join(res)

    print res
