import argparse
import sys
import subprocess

import autohdl.build as build
import autohdl.structure as structure
import autohdl.git as git
import autohdl.manager as hdlManager
import autohdl.pkg_info as pkg_info
import autohdl.documentation as documentation
from autohdl.hdlLogger import logging

alog = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(parents=[git.commands()], description='Helper to create designs')
    parser.add_argument('-doc', action='store_true', help='extended documentation in browser')
    parser.add_argument('-name', default='',
                        help='set design name and create structure [default - current directory name]')
    parser.add_argument('-version', action='store_true', help='display package version')
    parser.add_argument('-tb', action='store_true', help='export project to active-hdl')
    parser.add_argument('-edit', choices=['default_build', 'toolchain'], help='edit default build.yaml file')
    args = parser.parse_args()

    if args.version:
        print('AutoHDL version: ' + pkg_info.version())
    elif args.doc:
        documentation.handler('index')
    elif args.tb:
        hdlManager.kungfu()
    elif args.git:
        config = build.load()
        if not config:
            alog.info('Using default build.yaml (to see content: hdl.py -edit default_build)')
            config = build.default()
        config.update({'git': args.git})
        git.handle(config)
    elif args.edit:
        if args.edit == 'default_build':
            subprocess.Popen('notepad {}/Lib/site-packages/autohdl/data/build.yaml'.format(sys.prefix))
        elif args.edit == 'toolchain':
            subprocess.Popen('notepad {}/Lib/site-packages/autohdl_cfg/toolchain.yaml'.format(sys.prefix))
    else:
        dsn = structure.generate(path=args.name)
        git.initialize(args.name if args.name else '.')
        print(dsn)


if __name__ == '__main__':
    main()