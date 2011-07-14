import os
import lib.yaml as yaml

def load():
  path = os.path.join(os.path.dirname(__file__), 'data', 'pkg_info.yaml')
  with open(path, 'r') as f:
    content = yaml.load(f)
    return content

def dump(iContent):
  path = os.path.join(os.path.dirname(__file__), 'data', 'pkg_info.yaml')
  with open(path, 'w') as f:
    yaml.dump(iContent, f)



c = load()
c['version']['build'] = c['version']['build'] + 1
print c['version']['build']
print c
dump(c)

print load()

