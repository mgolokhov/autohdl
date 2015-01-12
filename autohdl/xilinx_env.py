import subprocess
import os
import logging
import locale

log = logging.getLogger(__name__)
from autohdl import toolchain


def get():
    try:
        wrapper = toolchain.Tool().get('ise_wrapper')
        encoding = locale.getdefaultlocale()[1]
        res = subprocess.check_output('cmd /c "call {0} & set"'.format(wrapper.replace('/', '\\')))
        res = res.decode(encoding)
        d = {}
        #create key=value environment variables
        for i in res.split(os.linesep):
            log.warning(i)
            res = i.split('=')
            if len(res) == 2:
                d.update({res[0]: res[1]})
        return d
    except Exception as exp:
        log.error(exp)
