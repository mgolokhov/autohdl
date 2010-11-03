import logging

log=logging.getLogger('hdlLogger')
log.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler(filename='hdlLogger.log',
                                  mode='w',
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

