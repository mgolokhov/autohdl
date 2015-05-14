import os
from autohdl.verilog import cache, vpreprocessor, vparser


def parse(fname):
    fdate = os.path.getmtime(fname)
    parsed = cache.load(fname, fdate)
    if parsed:
        return parsed
    with open(fname) as f:
        contents = f.read()
        preprocessed = vpreprocessor.Preprocessor(contents).result
        parsed = vparser.Parser(preprocessed).result
        cache.dump(fname, fdate, parsed)
        return parsed

if __name__ == '__main__':
    pass