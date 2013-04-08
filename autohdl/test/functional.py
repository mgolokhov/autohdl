import os
import shutil
import subprocess
import filecmp
import pprint
import time
# TODO: some relative path
import autohdl.structure as structure

def run():
    src = os.path.dirname(__file__)
    fake_repo = os.path.join(src, 'fake_repo')
    dst_fake_repo = os.path.join(os.getcwd(), 'fake_repo')
    if os.path.exists(dst_fake_repo):
        shutil.rmtree(dst_fake_repo)
    shutil.copytree(fake_repo, 'fake_repo')
    fake_repo_gold = os.path.join(src, 'fake_repo_gold')

    scripts = structure.search(dst_fake_repo, iOnly=['kungfu.py'])
    for s in scripts:
        startTest = time.clock()
        # path / fake_repo / dsn / script / kungfu.py
        pathAsList = s.replace('\\', '/').split('/')
        scriptFolder = '/'.join(pathAsList[:-1])
        os.chdir(scriptFolder)
        subprocess.call('python kungfu.py -tb')
        dsnName = pathAsList[-3]
        res = diff(fake_repo_gold + '/' + dsnName,
            dst_fake_repo + '/' + dsnName)
        pprint.pprint(res)
        print 'TEST____________', 'FAILED' if any(res.values()) else 'PASSED'
        print 'Run time ', time.clock() - startTest


def _getTree(iPath, iIgnoreExt=[]):
    res = set()
    start = iPath.replace('\\', '/') + '/'
    for root, dirs, files in os.walk(iPath):
        for f in files:
            if os.path.splitext(f)[1] not in iIgnoreExt:
                full = os.path.join(root, f).replace('\\', '/')
                leaf = full.split(start)[1]
                res.add(leaf)
    return res


def diff(iPathGold, iPathUUT, iIgnoreExt=['.pyc', '.adf', '.cfg']):
    gold = _getTree(iPathGold, iIgnoreExt)
    uut = _getTree(iPathUUT, iIgnoreExt)
    common = gold & uut
    only_gold = gold - uut
    only_uut = uut - gold
    diff_files = set()
    for i in common:
        if not filecmp.cmp(os.path.join(iPathGold, i),
            os.path.join(iPathUUT, i),
            shallow=False):
            diff_files.add(i)

    return {'diff_files': diff_files,
            'only_gold': only_gold,
            'only_uut': only_uut}


def cloneGoldRepo():
    src = os.path.dirname(__file__)
    fake_repo = os.path.join(src, 'fake_repo')
    if os.path.exists(fake_repo):
        shutil.rmtree(fake_repo)
    shutil.copytree(os.path.join(src, 'fake_repo_gold'),
        fake_repo)
    for root, dirs, files in os.walk(fake_repo):
        for dir in dirs:
            if dir in ['aldec', 'parsed']:
                shutil.rmtree(os.path.join(root, dir))
    print 'Cloned from gold repo'


if __name__ == '__main__':
    run()