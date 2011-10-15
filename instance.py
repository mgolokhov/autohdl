import os
import build

import verilog
from hdlLogger import log_call, logging
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
#  print files
  if files:
    if not isinstance(files, list):
      files = [files]
    for afile in files:
      if os.path.splitext(afile)[1] not in ['.v']:
        continue
      try:
        new = verilog.get_instances(afile)
        parsed.update(new)
      except IOError as e:
        log.debug(e)
        log.warning("Can't open file: "+afile)
  return parsed


@log_call
def resolve_undef(instance, in_file, _parsed = {}):
  if instance in _parsed:
    return {instance: _parsed[instance]}

  dep_file = build.getFile(iInstance = instance, iInFile = in_file)
  if dep_file:
    parsed = get_instances(dep_file)
    _parsed.update(parsed)
    if instance in parsed:
      return parsed
     
  dep_files = build.getFile() #return all cache
  if dep_files:
    parsed = get_instances([d for d in dep_files if os.path.splitext(d)[1] in ['.v']])
    _parsed.update(parsed)
    if instance in parsed:
      return {instance: parsed[instance]}


@log_call
def analyze(parsed, _ignore = set()):
  """
  Input: dictionary
  Output: dictionary
  """
  log.info('Analyzing...')
  _ignore.update(set(build.getParam(iKey='ignore_undefined_instances', iDefault=[])))
  for module in parsed:
    val = parsed[module]
    in_file = val['path']
    for instance in val['instances']:
      if instance not in _ignore and instance not in parsed:
        parsed_new = resolve_undef(instance, in_file)
        if not parsed_new:
          log.warning("Undefined instance="+instance+' in file='+os.path.abspath(in_file))
          _ignore.add(instance)
        else:
          return parsed_new
