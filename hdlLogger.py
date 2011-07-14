import logging
import sys
import os
import time

import socket
import logging.handlers
import subprocess

from lib.decorator import decorator


class MyLogger(logging._loggerClass):
  def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None):
    """Let the caller modify any of the parameters"""
    record = logging.LogRecord(name, level, fn, lno, msg, args, exc_info, func)
    if extra:
      for key in extra:
        record.__dict__[key] = extra[key]
    return record

logging.setLoggerClass(MyLogger)





socketHandler = logging.handlers.SocketHandler('localhost',
                                               logging.handlers.DEFAULT_TCP_LOGGING_PORT)
socketHandler.setLevel(logging.DEBUG)


consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
consoleFormatter = logging.Formatter("%(levelname)s:%(message)s")
consoleHandler.setFormatter(consoleFormatter)

# rootLogger
rootLogger = logging.getLogger('')
rootLogger.setLevel(logging.DEBUG)
rootLogger.addHandler(socketHandler)
rootLogger.addHandler(consoleHandler)



def toShortStr(obj, max=20):
  s = str(obj)
#  if len(s) > max:
#      return str(type(obj))
  return s


@decorator
def log_call(fn, *args, **kw):
  """Log calls to fn, reporting caller, args, and return value"""
  try:
    logger = logging.getLogger(fn.__module__)
    frame = sys._getframe(2)
    varnames = fn.func_code.co_varnames
    arglist = ', '.join([i[1]+'='+toShortStr(i[0]) for i in zip(args, varnames)])
    if kw:
      arglist += ', '.join(['{0}={1}'.format(k, v) for k, v in kw.viewitem()])
    
    logger.debug("%(func)s IN (%(args)s)" % (
                            {'func': fn.__name__,
                             'args': arglist,
                             }),
                        extra={
                            'filename': os.path.split(frame.f_code.co_filename)[-1],
                            'pathname': frame.f_code.co_filename,
                            'lineno': frame.f_lineno,
                            'module': fn.__module__,
                            'funcName': fn.__name__})
    
    result = fn(*args, **kw)

  except Exception as e:
    logger.exception(e)
    logger.debug('crashed')
    raise
  else:
    logger.debug("%(func)s OUT %(ret)s" % (
                          {'func': fn.__name__,
                           'ret': toShortStr(result),
                           }),
                      extra={
                          'filename': os.path.split(frame.f_code.co_filename)[-1],
                          'pathname': frame.f_code.co_filename,
                          'lineno': frame.f_lineno,
                          'module': fn.__module__,
                          'funcName': fn.__name__})

    
    
    
  return result


s = socket.socket()  #socket.AF_INET, socket.SOCK_STREAM
# check if logging server up, else - run
if s.connect_ex(('localhost', logging.handlers.DEFAULT_TCP_LOGGING_PORT)): #9020
  path = os.path.dirname(__file__) + '/log_server.py'
  subprocess.Popen('pythonw '+ path)



#log = logging.getLogger('')
