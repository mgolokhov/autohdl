import os
import pprint

from autohdl import build
from autohdl import verilog
from autohdl.hdlLogger import log_call, logging

log = logging.getLogger(__name__)


class InstanceException(Exception):
    def __init__(self, iString):
        Exception.__init__(self, iString)


@log_call
def get_instances(files):
    """
    Input: list of files;
    Output: dictionary
      module name:
        path     : file_path
        instances: set(instance1, instance2,..)
    """
    parsed = {}
    if files:
        if type(files) is not list:
            files = [files]
        for afile in files:
            if os.path.splitext(afile)[1] not in ['.v']:
                continue
            try:
                new = verilog.get_instances(afile)
                parsed.update(new)
            except IOError as e:
                log.debug(e)
                log.warning("Can't open file: " + afile)
    return parsed


@log_call
def resolve_undef(instance, in_file, _parsed={}):
#  print 'searching instance ', instance
#  print 'undef in file: ', in_file
    if instance in _parsed:
        return {instance: _parsed[instance]}

    dep_files = build.getDepPaths(in_file)
    if dep_files:
        for i in dep_files:
            parsed = get_instances([i])
            #      print parsed
            #      raw_input('next')
            for i in parsed:
                if i not in _parsed:
                #          print 'added'
                    _parsed[i] = parsed[i]
        if instance in _parsed:
            return {instance: _parsed[instance]}


def asNetlist(inFile, config):
    netlist = os.path.splitext(inFile)[0] + '.ngc'
    if os.path.exists(netlist):
        if config.get('depNetlist'):
            config['depNetlist'].append(netlist)
        else:
            config['depNetlist'] = [netlist]
        return True


@log_call
def analyze(parsed, config={}, _ignore=set()):
    """
    Input: dictionary
    Output: dictionary
    """
    #  _ignore.update(set(build.getParam(iKey='ignore_undefined_instances', iDefault=[])))
    for module in parsed:
        val = parsed[module]
        in_file = os.path.abspath(val['path'])
        for instance in val['instances']:
            if (instance, in_file) not in _ignore and instance not in parsed:
                parsed_new = resolve_undef(instance, in_file)
                if not parsed_new:
                    if not asNetlist(in_file, config):
                        log.warning("Undefined instance=" + instance + ' in file=' + in_file)
                    _ignore.add((instance, in_file))
                else:
                    return parsed_new
