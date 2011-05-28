# import from local src
import sys
import os
import shutil
import socket
import logging
import logging.handlers
import time


f = open('install.log', 'w')


attempt = 0
# 0 - connect ok
# 10061 no socket
# 10056 already binded
while True:
  f.write('shutting down log server...\n')
  s = socket.socket()
  if not s.connect_ex(('localhost', logging.handlers.DEFAULT_TCP_LOGGING_PORT)):
    rootLogger = logging.getLogger('')
    rootLogger.setLevel(logging.DEBUG)
    socketHandler = logging.handlers.SocketHandler('localhost',
                                                   logging.handlers.DEFAULT_TCP_LOGGING_PORT)
    rootLogger.addHandler(socketHandler)
    logging.warning('shutdown_log_server')
    attempt += 1
    time.sleep(1)
  else:
    f.write('log server were shut down\n')
    break
  if attempt == 10:
    break


#path = sys.prefix + '/Lib/site-packages/autohdl'
#
#if os.path.exists(path):
#  for root, dirs, files in os.walk(path):
#    for afile in files:
#      try:
#        os.remove(os.path.join(root, afile))
#      except WindowsError as e:
#        f.write(str(e)+'\n')
f.close()