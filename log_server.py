import cPickle
import logging
import logging.handlers
import SocketServer
import struct
import select
import socket
import time
import sys
import os


def shutdownLogServer():
  # 0 - connect ok
  # 10061 no socket
  # 10056 already binded
  for i in range(2):
    print 'shutting down log server...'
    s = socket.socket()
    time.sleep(2)
    if not s.connect_ex(('localhost', logging.handlers.DEFAULT_TCP_LOGGING_PORT)):
      rootLogger = logging.getLogger('')
      rootLogger.setLevel(logging.DEBUG)
      socketHandler = logging.handlers.SocketHandler('localhost',
                                                     logging.handlers.DEFAULT_TCP_LOGGING_PORT)
      rootLogger.addHandler(socketHandler)
      logging.warning('shutdown_log_server')
#      time.sleep(1)
    else:
      print 'log server were shut down'
      return
  print 'FAILED to shutdown log server'


class LogRecordStreamHandler(SocketServer.StreamRequestHandler):
    """Handler for a streaming logging request.

    This basically logs the record using whatever logging policy is
    configured locally.
    """

    def handle(self):
        """
        Handle multiple requests - each expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """
        while 1:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack(">L", chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = self.unPickle(chunk)
            record = logging.makeLogRecord(obj)
            if 'shutdown_log_server' in str(record):
                print record
                self.server.abort = True
            self.handleLogRecord(record)

    def unPickle(self, data):
        return cPickle.loads(data)

    def handleLogRecord(self, record):
        # if a name is specified, we use the named logger rather than the one
        # implied by the record.
        if self.server.logname is not None:
            name = self.server.logname
        else:
            name = record.name
        logger = logging.getLogger(name)
        # N.B. EVERY record gets logged. This is because Logger.handle
        # is normally called AFTER logger-level filtering. If you want
        # to do filtering, do it at the client end to save wasting
        # cycles and network bandwidth!
        logger.handle(record)


class LogRecordSocketReceiver(SocketServer.ThreadingTCPServer):
    """simple TCP socket-based logging receiver suitable for testing.
    """

    
    
    def __init__(self, host='localhost',
                 port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
                 handler=LogRecordStreamHandler):
        SocketServer.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.abort = 0
        self.timeout = 1
        self.logname = None
        self.allow_reuse_address = 1
 
    def serve_until_stopped(self):
        abort = 0
        while not abort:
            rd, wr, ex = select.select([self.socket.fileno()],
                                       [], [],
                                       1)
            if rd:
                self.handle_request()
            abort = self.abort

            
            
def main():
    alog = logging.getLogger('')
    
    # Add the log message handler to the logger
    path = sys.prefix + '/Lib/site-packages/autohdl_cfg/autohdl.log'
    dir = sys.prefix + '/Lib/site-packages/autohdl_cfg/'
    if not os.path.exists(dir):
      os.mkdir(dir)
    fileHandler = logging.handlers.RotatingFileHandler(
                                                      path,
                                                      maxBytes=20000000,
                                                      backupCount=1)
    fileHandler.setLevel(level=logging.DEBUG)
    fileFormatter = logging.Formatter("%(asctime)s:%(filename)s:%(lineno)d:%(levelname)s:%(message)s")
    fileHandler.setFormatter(fileFormatter)
    alog.addHandler(fileHandler)  

    tcpserver = LogRecordSocketReceiver()
    tcpserver.serve_until_stopped()

    
if __name__ == "__main__":
    main()