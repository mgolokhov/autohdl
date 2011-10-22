buildYaml = '''\
build.yaml info:
1. Some sort of base class for all configurations in the current design.
   Every field(1*) can be redefined in script (e.g. kungfu.py)
2. "dep" field is very important for dependency analyze,
   because location of build.yaml predefined.

1* for "dep" field - script adds new paths, so extends dep list in build.yaml
   after first run.
'''