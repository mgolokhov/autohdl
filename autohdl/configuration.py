import pprint
import logging
import sys
import os
from copy import deepcopy
import re
import shutil
import importlib

from autohdl import FILE_USER_CFG, FILE_DEFAULT_CFG

alog = logging.getLogger(__name__)


def load_default_cfg():
    sys.path.append(os.path.dirname(FILE_DEFAULT_CFG))
    module_with_default_cfg = os.path.splitext(os.path.basename(FILE_DEFAULT_CFG))[0]
    return importlib.import_module(module_with_default_cfg).cfg


def load_user_cfg():
    sys.path.append(os.path.dirname(FILE_USER_CFG))
    module_with_user_cfg = os.path.splitext(os.path.basename(FILE_USER_CFG))[0]
    return importlib.import_module(module_with_user_cfg).cfg


def dump_relative_paths(cfg):
    cfg_old = deepcopy(cfg)
    convert_to_relative(cfg)
    if cfg != cfg_old:
        main_script = sys.modules['__main__'].__file__
        with open(main_script) as f:
            contents = f.read()
            for p, r in zip(cfg_old['src'], cfg['src']):
                if p != r:
                    contents = re.sub(pattern=p, repl=r, string=contents, flags=re.MULTILINE | re.S)
            for p, r in zip(cfg_old['include_paths'], cfg['include_paths']):
                if p != r:
                    contents = re.sub(pattern=p, repl=r, string=contents, flags=re.MULTILINE | re.S)
        # TODO: thorough test before dump
        with open(main_script, 'w') as f:
            f.write(contents)


def convert_to_relative(cfg):
    d = {'src': [], 'include_paths': []}
    for k in d:
        for i in cfg[k]:
            if not os.path.exists(i):
                sys.exit("Wrong path {}, cwd = {}".format(i, os.getcwd()))
            afile = os.path.relpath(i).replace('\\', '/')
            if not os.path.exists(afile):
                sys.exit("Wrong path {}, cwd = {}".format(afile, os.getcwd()))
            d[k].append(afile)
    cfg.update(d)


def convert_to_abs(cfg):
    d = {'src': [], 'include_paths': []}
    for k in d:
        for i in cfg[k]:
            if not os.path.exists(i):
                sys.exit("Wrong path {}, cwd = {}".format(i, os.getcwd()))
            if os.path.isabs(i):
                continue
            afile = os.path.abspath(i).replace('\\', '/')
            if not os.path.exists(afile):
                sys.exit("Wrong path {}, cwd = {}".format(afile, os.getcwd()))
            d[k].append(afile)
    cfg.update(d)


def load_env(cfg):
    cfg['cwd'] = os.getcwd()
    cfg['dsn_root'] = os.path.dirname(os.getcwd())
    cfg['dsn_name'] = os.path.basename(cfg['dsn_root'])


def load(script_cfg, command_line_cfg):
    result_cfg = {}
    load_env(result_cfg)
    default_cfg = load_default_cfg()
    user_cfg = load_user_cfg()
    alog.debug('Script config:\n ' + pprint.pformat(script_cfg))

    result_cfg.update(default_cfg)
    result_cfg.update(user_cfg)
    result_cfg.update(script_cfg)
    # pprint.pprint(vars(command_line_cfg))
    {result_cfg.update({k: v}) for k, v in vars(command_line_cfg).items() if v}
    if command_line_cfg.mcs:
        result_cfg.update({'eeprom_kilobytes': command_line_cfg.mcs})

    dump_relative_paths(result_cfg)
    convert_to_abs(result_cfg)
    return result_cfg


def copy():
    dst = FILE_DEFAULT_CFG
    src = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'kungfu.py')
    folder = os.path.dirname(dst)
    if not os.path.exists(folder):
        os.makedirs(folder)
    shutil.copy(src, dst)

    dst = FILE_USER_CFG
    if not os.path.exists(dst):
        folder = os.path.dirname(dst)
        if not os.path.exists(folder):
            os.makedirs(folder)
        shutil.copy(src, dst)




