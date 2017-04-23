import os
import shutil
from collections import namedtuple

from autohdl import PREDEFINED_DIRS, FILE_USER_CFG, IGNORE_REPO_DIRS
from autohdl import verilog
import logging

alog = logging.getLogger(__name__)


def generate(path=''):
    # create dir structure
    # copy config file
    # return printable tree structure
    root = os.path.abspath(path)
    if not os.path.exists(root):
        os.makedirs(root)
    alog.info('Design root: ' + root)
    for i in PREDEFINED_DIRS:
        path = os.path.join(root, i)
        if not os.path.exists(path):
            os.mkdir(path)
    autohdl_cfg = FILE_USER_CFG
    Copy = namedtuple('Copy', ['src', 'dst'])
    list_to_copy = (
        Copy(autohdl_cfg, os.path.join(root, 'script', 'kungfu.py')),
    )
    for i in list_to_copy:
        if not os.path.exists(i.dst):
            shutil.copy(i.src, i.dst)
    return get(root)


def get(path='', ignore=IGNORE_REPO_DIRS):
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


def _convert_to_set(arg):
    arg = arg or set()
    if type(arg) is str:
        arg = [arg]
    return set(arg)


def search(directory='.',
           ignore_dir=None, ignore_ext=None, only_ext=None):
    """
      Recursively search files by pattern.
      Input: directory - start point to search,
             ignore and only - filter patterns for directory and files (should be lists)
      Returns list of files.
    """
    ignore_dir = _convert_to_set(ignore_dir)
    ignore_ext = _convert_to_set(ignore_ext)
    only_ext = _convert_to_set(only_ext)

    res_files = []
    for root, dirs, files in os.walk(os.path.abspath(directory)):
        for i in set(dirs) & ignore_dir:
            alog.debug('ignore directory: ' + i)
            dirs.remove(i)
        for f in files[:]:
            alog.debug('file: ' + f)
            ext = os.path.splitext(f)[1]
            if ext in ignore_ext:
                files.remove(f)
                alog.debug('ignore file (ignore list) ' + f)
            elif only_ext and (ext not in only_ext):
                files.remove(f)
                alog.debug('ignore file (only list) ' + f)
            else:
                alog.debug('add file ' + f)
                res_files.append(os.path.join(root, f))
    return res_files  # [i.replace('\\', '/') for i in res_files]


def parse(src_files):
    # input: list of source files
    # output: dict
    # {abs_file_path:
    #   tuple(module_name0: set(inst1, inst2, ...),
    #         module_name1: set(inst1, inst2, ...),
    #        ...
    #        )
    #  abs_file_path2:
    #   ...
    # }
    d = {}
    for afile in src_files:
        with open(afile) as f:
            d.update(verilog.parse(f.read()))
    return d


if __name__ == '__main__':
    pass