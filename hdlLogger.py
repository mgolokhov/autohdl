import logging
import sys
import os
import time
from autohdl.lib.decorator import decorator

log=logging.getLogger('hdlLogger')
log.setLevel(logging.DEBUG)


try:
  if os.path.exists('hdlLogger.log') and\
     time.time() - os.path.getmtime('hdlLogger.log') > 30:
    os.remove('hdlLogger.log')
except OSError as e:
  log.warning(e)
  
fileHandler = logging.FileHandler(filename='hdlLogger.log',
                                  mode='a',
                                  delay=True)
fileHandler.setLevel(level=logging.DEBUG)
fileFormatter = logging.Formatter("%(filename)s:%(lineno)d:%(levelname)s:%(message)s")
fileHandler.setFormatter(fileFormatter)
log.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
consoleFormatter = logging.Formatter("%(levelname)s:%(message)s")
consoleHandler.setFormatter(consoleFormatter)
log.addHandler(consoleHandler)



def toShortStr(obj, max=20):
  s = str(obj)
#  if len(s) > max:
#      return str(type(obj))
  return s


@decorator
def log_call(fn, *args, **kw):
  """Log calls to fn, reporting caller, args, and return value"""
  try:
    frame = sys._getframe(2)
    varnames = fn.func_code.co_varnames
    arglist = ', '.join([i[1]+'='+toShortStr(i[0]) for i in zip(args, varnames)])
    if kw:
      arglist += ', '.join(['{0}={1}'.format(k, v) for k, v in kw.viewitem()])
    
    log.debug("{file} {line} {func} IN ({args})".format(
                              file = os.path.split(frame.f_code.co_filename)[1],
                              line = frame.f_lineno,
                              func = fn.__name__,
                              args = arglist))
    result = fn(*args, **kw)

  except Exception as e:
    log.exception(e)
    log.debug('crashed')
    raise
  else:
    log.debug('{func} OUT {res}'.format(func = fn.__name__,
                                        res = toShortStr(result)))
    
  return result

