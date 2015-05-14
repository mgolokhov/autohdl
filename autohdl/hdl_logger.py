import logging
import sys
import os
import socket
import logging.handlers
import subprocess
import logging.config as lc

from decorator import decorator


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s:%(filename)s:%(lineno)d:%(levelname)s:%(message)s'
        },
        'simple': {
            'format': '%(levelname)s: %(message)s'
        },
    },
    'handlers': {
        'consoleDebug': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'consoleInfo': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'socket': {
            'level': 'DEBUG',
            'class': 'logging.handlers.SocketHandler',
            'host': 'localhost',
            'port': logging.handlers.DEFAULT_TCP_LOGGING_PORT,
        },
    },
    'loggers': {
        '': {
            'handlers': ['consoleInfo', 'socket'],
            'level': 'DEBUG',
        },
    }
}

lc.dictConfig(LOGGING)

s = socket.socket()  #socket.AF_INET, socket.SOCK_STREAM
# check if logging server up, else - run
if s.connect_ex(('localhost', logging.handlers.DEFAULT_TCP_LOGGING_PORT)): #9020
    path = os.path.dirname(__file__) + '/log_server.py'
    p = subprocess.Popen('pythonw ' + path)


class MyLogger(logging._loggerClass):
    def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None):
        """Let the caller modify any of the parameters"""
        record = logging.LogRecord(name, level, fn, lno, msg, args, exc_info, func)
        if extra:
            for key in extra:
                record.__dict__[key] = extra[key]
        return record


#logging.setLoggerClass(MyLogger)


@decorator
def log_call(fn, *args, **kw):
    """Log calls to fn, reporting caller, args, and return value"""
    logger = logging.getLogger(fn.__module__)
    try:
        frame = sys._getframe(2)
        varnames = fn.__code__.co_varnames
        arglist = ', '.join([i[1] + '=' + str(i[0]) for i in zip(args, varnames)])
        if kw:
            arglist += ', '.join(['{0}={1}'.format(k, v) for k, v in kw.items()])

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
             'ret': str(result),
            }),
            extra={
                'filename': os.path.split(frame.f_code.co_filename)[-1],
                'pathname': frame.f_code.co_filename,
                'lineno': frame.f_lineno,
                'module': fn.__module__,
                'funcName': fn.__name__})

    return result



