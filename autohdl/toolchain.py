import ctypes
import fnmatch
import os
import json
import glob
import logging

from autohdl import FILE_TOOLCHAIN_CFG
from autohdl import progress_bar

alog = logging.getLogger(__name__)




class Tool(object):
    def __init__(self):
        self.data = {'ise': {'gui': 'ise.exe',
                             'impact': 'impact.exe',
                             'batch': 'xtclsh.exe',
                             'xflow': 'xflow.exe',
                             'promgen': 'promgen.exe',
                             'wrapper': 'settings??.bat',
                             'path': ['/Xilinx/']},
                     'synplify': {'gui': 'synplify_premier.exe',
                                  'batch': 'synplify_premier.exe',
                                  'path': ['/Synopsys/', '/Synplicity/']},
                     }
        self.path_config = FILE_TOOLCHAIN_CFG
        self.result = None
        self.tag = None
        self.metadata = None

    def create_config(self):
        if not os.path.exists(self.path_config):
            adir = os.path.dirname(self.path_config)
            if not os.path.exists(adir):
                os.mkdir(adir)
            open(self.path_config, 'w').close()

    def check_metadata(self, tag):
        self.tag = tag
        try:
            self.tool, self.mode = tag.split('_')
            self.metadata = self.data[self.tool]['path']
        except Exception as e:
            alog.debug(e)
            raise KeyError('Wrong tag ' + tag)

    def get(self, tag):
        """
        Input: tool_mode
        internally form tag, tool, mode, paths
        """
        # try toolchain.yaml
        # else search
        # dump to toolchain.yaml
        self.check_metadata(tag)
        path = self.get_from_cfg(tag)
        if path:
            return path
        self.search_light()
        return self.result

    def refresh(self, tag=''):
        if tag:
            self.check_metadata(tag)
            self.get_from_cfg(tag)
            self.search_light()
            return self.result
        else:
            try:
                os.remove(self.path_config)
            except IOError as e:
                alog.debug(e)

    def get_from_cfg(self, tag):
        self.cfg = {}
        try:
            self.create_config()
            with open(self.path_config) as f:
                self.cfg = json.load(f)
                path = self.cfg[tag]
        except Exception as e:
            alog.debug(e)
            return False
        if os.path.exists(path):
            return path
        return False

    def getWin32Drivers(self):
        drivers = []
        LOCALDISK = 3
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for i in range(26):
            if (bitmask >> i) & 0x01:
                driver = chr(i + 65) + ':/'
                if ctypes.windll.kernel32.GetDriveTypeW(driver) == LOCALDISK:
                    drivers.append(driver)
        return drivers

    def find_files(self, directory, pattern):
        for root, dirs, files in os.walk(directory):
            for basename in files:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)
                    yield filename

    def search_light(self):
        alog.info('Searching {}...'.format(self.tag))
        logicDrives = self.getWin32Drivers()
        paths = self.metadata
        rootDirs = []
        for logicDrive in logicDrives:
            for path in paths:
                for nested in ['', '/*/', '/*/' * 2, '/*/' * 3]:
                    rootDirs += glob.glob('{drive}{nested}{path}'.format(drive=logicDrive, nested=nested, path=path))
        self.fullPaths = []
        for i in rootDirs:
            for nested in ['', '/*/', '/*/' * 2, '/*/' * 3, '/*/' * 4, '/*/' * 5, '/*/' * 6]:
                self.fullPaths += glob.glob('{0}{1}{2}'.format(i, nested, self.data[self.tool][self.mode]))
        progress_bar.stop()
        if self.fullPaths:
            self.fullPaths = [i.replace('\\', '/') for i in self.fullPaths]
            self.fullPaths.sort(key=lambda f: os.path.getmtime(f), reverse=True)
            self.ask_confirm()
            self.save_search_result()
        else:
            alog.warning('Cant find tool: ' + self.tag)


    def save_search_result(self):
        try:
            if not self.cfg:
                self.cfg = dict()
            with open(self.path_config, 'w') as f:
                self.cfg.update({self.tag: '{}'.format(self.result)})
                json.dump(self.cfg, f, indent=2)
        except IOError as exp:
            alog.error(exp)
            return


    def ask_confirm(self):
        d = dict([(index, path) for index, path in enumerate(self.fullPaths)])
        current = 0
        while True:
            print('\nFound paths (in use [*]):')
            for k, v in d.items():
                if current == k:
                    print('[*] {}'.format(v))
                else:
                    print('[{0}] {1}'.format(k, v))
            num = input('To change enter number. Leave as is and continue hit Enter:')
            if not num:
                self.result = d[current]
                return
            try:
                if int(num) <= len(d):
                    current = int(num)
            except ValueError as exp:
                alog.debug(exp)
                print('Invalid input!')


if __name__ == '__main__':
    #Tool().refresh('ise_xflow')
    print(Tool().get('ise_impact'))
    print(Tool().get('ise_xflow'))
    print(Tool().get('synplify_batch'))
    print(Tool().get('synplify_gui'))
    print(Tool().get('synplify_gui'))
    print(Tool().get('ise_gui'))
    print(Tool().get('ise_batch'))
    print(Tool().get('ise_xflow'))

