import zipfile
import os

import pkg_info

os.chdir('..')
zipFileName = 'autohdl-' + pkg_info.incBuild()+ '.zip'

myZipFile = zipfile.ZipFile(zipFileName, "w" )
for root, dirs, files in os.walk('autohdl'):
  if 'test' in dirs:
    dirs.remove('test')
  for f in files:
    path = os.path.join(root,f)
    #TODO: win specific, add nix style
    if '\.' in path or os.path.splitext(f)[1] in ['.pyc', '.pyo']:
      continue
    print path
    myZipFile.write(path, path, zipfile.ZIP_DEFLATED)
myZipFile.write('autohdl/install.py', 'install.py', zipfile.ZIP_DEFLATED)  
myZipFile.close()

print 'Generation done: ', zipFileName