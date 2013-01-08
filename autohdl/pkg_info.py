import os
import json


def load():
    ver_fp = os.path.join(os.path.dirname(__file__), 'data', 'version.json')
    with open(ver_fp) as f:
        data = json.load(f)
        return ver_fp, data

def version():
    _, ver = load()
    return '{}.{}.{}'.format(ver['major'], ver['minor'], ver['build'])


def inc_version():
    ver_fp, ver = load()
    ver['build'] += 1
    with open(ver_fp, 'w') as f:
        f.write(json.dumps(ver))
    return version()

