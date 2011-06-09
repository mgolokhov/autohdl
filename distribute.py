import zipfile
import os
import database

os.chdir('..')
zipFileName = 'autohdl-' + database.incBuildVersion()+ '.zip'

myZipFile = zipfile.ZipFile(zipFileName, "w" )
for root, dirs, files in os.walk('autohdl'):
  for f in files:
    path = os.path.join(root,f)
    #BUGAGA win specific
    if '\.' in path or os.path.splitext(f)[1] in ['.pyc', '.pyo']:
      continue
    print path
    myZipFile.write(path, path, zipfile.ZIP_DEFLATED)
myZipFile.write('autohdl/install.py', 'install.py', zipfile.ZIP_DEFLATED)  
myZipFile.close()