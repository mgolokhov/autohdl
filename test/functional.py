import os
import shutil
import subprocess
import filecmp
import pprint

def run():
  src = os.path.dirname(__file__)
  fake_repo = os.path.join(src,'fake_repo')
  dst_fake_repo = os.path.join(os.getcwd(),'fake_repo')
  if os.path.exists(dst_fake_repo):
    shutil.rmtree(dst_fake_repo)
  shutil.copytree(fake_repo, 'fake_repo')

  os.chdir('fake_repo/dsn1/script')
  subprocess.call('python kungfu.py -tb')
  fake_repo_gold = os.path.join(src, 'fake_repo_gold')
  res = diff(fake_repo_gold, dst_fake_repo)
  pprint.pprint(res)

def _getTree(iPath, iIgnoreExt = []):
  res = set()
  start = iPath.replace('\\', '/')+'/'
  for root, dirs, files in os.walk(iPath):
    for f in files:
      if os.path.splitext(f)[1] not in iIgnoreExt:
        full = os.path.join(root, f).replace('\\', '/')
        leaf = full.split(start)[1]
        res.add(leaf)
  return res


def diff(iPathGold, iPathUUT, iIgnoreExt = ['.pyc', '.adf', '.cfg']):
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
          'only_gold' : only_gold,
          'only_uut'  : only_uut}


def cloneGoldRepo():
  src = os.path.dirname(__file__)
  fake_repo = os.path.join(src,'fake_repo')
  if os.path.exists(fake_repo):
    shutil.rmtree(fake_repo)
  shutil.copytree(os.path.join(src,'fake_repo_gold'),
                  fake_repo)
  for root, dirs, files in os.walk(fake_repo):
    for dir in dirs:
      if dir in ['aldec', 'parsed']:
        shutil.rmtree(os.path.join(root, dir))
  print 'Cloned from gold repo'


if __name__ == '__main__':
  cloneGoldRepo()