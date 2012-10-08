import sys
import time

for i in range(5):
  print 'some info in stdout'
  sys.stderr.write('some info in stderr\n')
  time.sleep(1)
sys.exit(1)