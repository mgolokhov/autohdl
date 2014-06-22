import copy
import hashlib
import subprocess
import sys
import shutil
import os
import threading
import time

from autohdl import build, hdlGlobals
from autohdl.hdlLogger import logging
from autohdl.hdlGlobals import aldecPath


alog = logging.getLogger(__name__)
alog.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
consoleFormatter = logging.Formatter("%(levelname)s:%(message)s")
consoleHandler.setFormatter(consoleFormatter)
alog.addHandler(consoleHandler)


def calcSha(afile):
    with open(afile) as f:
        h = hashlib.sha1()
        h.update(f.read().encode('utf-8'))
        return h.hexdigest()


def isModified(src, dst):
    if not os.path.exists(dst):
        return True
    if os.stat(src).st_mtime == os.stat(dst).st_mtime:
        return
    if calcSha(src) == calcSha(dst):
        return
    return True


def syncRepo(move=False):
# cwd = <dsnName>/script
#  alog.debug('Wazzzup!')
    rootPathAldec = aldecPath + '/src/'
    rootPathDsn = '../'
    syncDirs = [d for d in os.listdir(rootPathAldec)
                if d not in ['.svn', '.git'] and d in os.listdir(rootPathDsn)]
    for dir in syncDirs:
        for root, dirs, files in os.walk(rootPathAldec + dir):
            try:
                dirs[:] = [d for d in dirs if d not in ['.svn', '.git']]
                pathDsn = root.replace(rootPathAldec, rootPathDsn)
                if not os.path.exists(pathDsn):
                    os.makedirs(pathDsn)
                for f in files:
                    src = os.path.abspath(root + '/' + f)
                    dst = os.path.abspath(pathDsn + '/' + f)
                    if move:
                        alog.info('Move src={0} dst={1}'.format(src, dst))
                        shutil.move(src, dst)
                    elif isModified(src, dst):
                        alog.info('Copy src={0} dst={1}'.format(src, dst))
                        shutil.copyfile(src, dst)
            except Exception as e:
                alog.exception(e)


def copyInRepo():
    while True:
        syncRepo()
        time.sleep(1)


def moveInRepo():
    syncRepo(move=True)


def parse(content):
    d = set()
    files = [i for i in content.splitlines() if '[file:' in i or 'Enabled' in i]
    for i, l in enumerate(files):
        if l == 'Enabled=1':
            d.add(files[i - 1])
        elif l == 'Enabled=0':
            alog.debug(str(files[i - 1]))
    return d


def testBenchF(testBench):
    try:
        fi = [i for i in testBench if os.path.splitext(i)[1] == '.v']
        with open(fi[0]) as f:
            context = f.read()
        res = []
        rst = None
        for i in ['iRst', 'rst', 'RST', 'Rst', 'reset', 'Reset']:
            if i in context:
                rst = i
        clk = None
        for i in ['iClk', 'clk', 'Clk', 'Clock', 'clock']:
            if i in context:
                clk = i
        for i in context.splitlines():
            if '`timescale' in i:
                res.append('`timescale 1ns/1ns')
            elif 'initial' in i:
                if clk:
                    res.append(('initial begin\n'
                                '    {clk} = 0;\n'
                                '    forever #1ns {clk} = !{clk};\n'
                                'end\n').format(clk=clk))
                if rst:
                    res.append(('initial begin\n'
                                '    {rst} = 1;\n'
                                '    #33ns {rst} = 0;\n'
                                'end').format(rst=rst))
            elif '$monitor' in i:
                pass
            else:
                res.append(i)
            with open(fi[0], 'w') as f:
                f.write('\n'.join(res))

    except Exception as e:
        pass


def updateDeps(files):
    files = [os.path.abspath(aldecPath + f[7:-1]) for f in files]
    testBench = [i for i in files if '\\aldec\\src\\TestBench\\' in i]
    #  testBenchF(testBench)
    files = [i for i in files
             if ('\\aldec\\src\\' not in i
                 and '\\aldec\\src\\src\\' not in i
                 and 'TestBenchUtils' not in i)]
    files = [i for i in files if os.path.splitext(i)[1] in hdlGlobals.hdlFileExt]
    build.updateDeps(files)


def synchBuild():
    # relative to dsn/script dsn/aldec/config.cfg
    config = os.path.abspath(aldecPath + '/compile.cfg')
    files = set()
    shaOld = None
    while True:
        try:
            with open(config) as f:
                content = f.read()
                h = hashlib.sha1()
                h.update(content.encode('utf-8'))
                shaNew = h.hexdigest()
                if shaNew != shaOld:
                    filesNew = parse(content)
                    added = filesNew - files
                    if files and added:
                        alog.debug('Added: ' + str(added))
                        updateDeps(added)
                    files = copy.copy(filesNew)
        except (IOError, WindowsError) as e:
            alog.error('Cant open file: ' + config)
            alog.exception(e)
        time.sleep(1)


alog.debug(str(sys.argv))
os.chdir(sys.argv[1])

b = threading.Thread(target=copyInRepo)
b.setDaemon(1)
b.start()

c = threading.Thread(target=synchBuild)
c.setDaemon(1)
c.start()

aldec = sys.argv[2] #toolchain.getPath(iTag = 'avhdl_gui')
subprocess.call([aldec, aldecPath + '/wsp.aws'])
moveInRepo()

sys.exit()


