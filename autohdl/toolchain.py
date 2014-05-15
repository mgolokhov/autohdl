import ctypes
import fnmatch
import os
import sys
import glob

from autohdl.hdlLogger import log_call, logging

alog = logging.getLogger(__name__)

import yaml as yaml
from yaml.error import YAMLError
import autohdl.progressBar as progressBar


class Tool(object):
    #@log_call
    def __init__(self):
        self.data = {'avhdl': {'gui': 'avhdl.exe',
                               'batch': None,
                               'path': ['/Aldec/']},
                     'ise': {'gui': 'ise.exe',
                             'impact': 'impact.exe',
                             'batch': 'xtclsh.exe',
                             'xflow': 'xflow.exe',
                             'promgen': 'promgen.exe',
                             'wrapper': 'settings??.bat',
                             'path': ['/Xilinx/']},
                     'synplify': {'gui': 'synplify_premier.exe',
                                  'batch': 'synplify_premier.exe',
                                  'path': ['/Synopsys/', '/Synplicity/']},
                     # tested on version Git-1.7.4-preview20110204
                     'git': {'batch': 'git.exe',
                             'sh': 'sh.exe',
                             'path': ['/Git/']}
                     }
        self.pathCfg = sys.prefix + '/Lib/site-packages/autohdl_cfg/toolchain.yaml'
        if not os.path.exists(self.pathCfg):
            adir = os.path.dirname(self.pathCfg)
            if not os.path.exists(adir):
                os.mkdir(adir)
            open(self.pathCfg, 'w').close()
        self.result = None


    def checkTag(self, tag):
        self.tag = tag
        try:
            self.tool, self.mode = tag.split('_')
            self.paths = self.data[self.tool]['path']
            self.util = self.data[self.tool][self.mode]
        except Exception as e:
            print e
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
        self.checkTag(tag)
        path = self.getFromCfg()
        if path:
            return path
        self.searchLight()
        return self.result


    def refresh(self, tag=''):
        if tag:
            self.checkTag(tag)
            self.getFromCfg()
            self.searchLight()
            return self.result
        else:
            try:
                os.remove(self.pathCfg)
            except IOError as e:
                alog.debug(e)


    #@log_call
    def getFromCfg(self):
        self.cfg = {}
        try:
            with open(self.pathCfg, 'r') as f:
                self.cfg = yaml.load(f)
                path = self.cfg[self.tag]
        except Exception as e:
            print e
            alog.debug(e)
            return False

        if os.path.exists(path):
            return path

        return False


    #@log_call
    def getWin32Drivers(self):
        drivers = []
        LOCALDISK = 3
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for i in range(26):
            if (bitmask >> i) & 0x01:
                driver = chr(i + 65) + ':/'
                if ctypes.windll.kernel32.GetDriveTypeA(driver) == LOCALDISK:
                    drivers.append(driver)
        return drivers


    def find_files(self, directory, pattern):
        for root, dirs, files in os.walk(directory):
            for basename in files:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)
                    yield filename

    #@log_call
    def searchLight(self):
        alog.info('Searching {}...'.format(self.tag))
        progressBar.run()
        logicDrives = self.getWin32Drivers()
        paths = self.paths
        rootDirs = []
        for logicDrive in logicDrives:
            for path in paths:
                for nested in ['', '/*/', '/*/' * 2, '/*/' * 3]:
                    rootDirs += glob.glob('{drive}{nested}{path}'.format(drive=logicDrive, nested=nested, path=path))
        self.fullPaths = []
        for i in rootDirs:
            for nested in ['', '/*/', '/*/' * 2, '/*/' * 3, '/*/' * 4, '/*/' * 5, '/*/' * 6]:
                self.fullPaths += glob.glob('{0}{1}{2}'.format(i, nested, self.util))
        progressBar.stop()
        if self.fullPaths:
            self.fullPaths = [i.replace('\\', '/') for i in self.fullPaths]
            self.fullPaths.sort(cmp=None, key=os.path.getmtime, reverse=True)
            self.askConfirm()
            self.saveSearchResult()
        else:
            alog.warning('Cant find tool: ' + self.tag)


    #@log_call
    def saveSearchResult(self):
        try:
            if not self.cfg:
                self.cfg = dict()
            with open(self.pathCfg, 'w') as f:
                self.cfg.update({self.tag: '{}'.format(self.result)})
                yaml.dump(self.cfg, f, default_flow_style=False)
        except (IOError, YAMLError) as exp:
            alog.error(exp)
            return


    #@log_call
    def askConfirm(self):
        d = dict([(index, path) for index, path in enumerate(self.fullPaths)])
        current = 0
        while True:
            print '\nFound paths (in use [*]):'
            for k, v in d.iteritems():
                if current == k:
                    print '[*] {}'.format(v)
                else:
                    print '[{0}] {1}'.format(k, v)
            num = raw_input('To change enter number. Leave as is and continue hit Enter:')
            if not num:
                self.result = d[current]
                return
            try:
                if int(num) <= len(d):
                    current = int(num)
            except ValueError as exp:
                alog.debug(exp)
                print 'Invalid input!'


if __name__ == '__main__':
    Tool().refresh('ise_xflow')
#  print Tool().get('ise_impact')
#  print Tool().get('ise_xflow')
#  print Tool('avhdl_gui').result
#  print Tool('synplify_batch').result
#  print Tool('git_batch').result
#  print Tool('synplify_gui').result
#  print Tool('ise_gui').result
#  print Tool('ise_batch').result
#  print Tool('ise_xflow').result

