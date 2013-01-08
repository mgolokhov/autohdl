import subprocess

import logging

log = logging.getLogger(__name__)
from autohdl import toolchain


def get():
    try:
        wrapper = toolchain.Tool().get('ise_wrapper')

        res = subprocess.check_output('cmd /c "call {0} & set"'.format(wrapper.replace('/', '\\')))

        d = {}
        #create key=value environment variables
        for i in res.split('\r\n'):
            res = i.split('=')
            if len(res) == 2:
                d.update({res[0]: res[1]})
        return d
    except Exception as exp:
        log.error(exp)
