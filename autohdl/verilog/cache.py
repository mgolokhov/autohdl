import os
import json
from autohdl.hdl_globals import FILE_CACHE


def load(fname, fdate):
    if os.path.exists(FILE_CACHE):
        with open(FILE_CACHE) as f:
            contents = json.load(f)
            parsed = contents.get(fname)
            if parsed and parsed['fdate'] == fdate:
                print('hit file cache')
                return parsed


def dump(fname, fdate, parsed):
    cache = {}
    parsed['fdate'] = fdate
    d = {fname: parsed}
    if os.path.exists(FILE_CACHE):
        with open(FILE_CACHE) as f:
            cache = json.load(f)
    else:
        os.makedirs(os.path.dirname(FILE_CACHE))
    cache.update(d)
    with open(FILE_CACHE, 'w') as f:
        json.dump(cache, f, indent=2)
    print("miss file cache")

