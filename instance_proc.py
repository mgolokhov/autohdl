import instance
import sys


from hdlLogger import log_call, logging
log = logging.getLogger(__name__)

print instance.ParseFile(sys.argv[1]).getResult()
