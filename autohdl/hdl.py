import argparse
import sys
import subprocess

import autohdl.structure as structure
import autohdl.pkg_info as pkg_info
import autohdl.documentation as documentation
from autohdl.hdl_logger import logging
import autohdl.configuration as configuration

alog = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Helper to create designs')
    parser.add_argument('-doc', action='store_true', help='extended documentation in browser')
    parser.add_argument('-name', default='',
                        help='set design name and create structure [default - current directory name]')
    parser.add_argument('-version', action='store_true', help='display package version')
    parser.add_argument('-edit', choices=['default_build', 'toolchain'], help='edit default build.yaml file')
    args = parser.parse_args()

    if args.version:
        print('AutoHDL version: ' + pkg_info.version())
    elif args.doc:
        documentation.handler('index')
    elif args.edit:
        if args.edit == 'default_build':
            subprocess.Popen('notepad {}/Lib/site-packages/autohdl/data/build.yaml'.format(sys.prefix))
        elif args.edit == 'toolchain':
            subprocess.Popen('notepad {}/Lib/site-packages/autohdl_cfg/toolchain.yaml'.format(sys.prefix))
    else:
        dsn = structure.generate(path=args.name)
        print(dsn)


if __name__ == '__main__':
    configuration.copy()
    main()