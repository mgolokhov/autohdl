import argparse
import logging
import os
import pprint
import subprocess

alog = logging.getLogger(__name__)

import autohdl.build as build
import autohdl.structure as structure
import autohdl.toolchain as toolchain
import autohdl.git as git
import autohdl.hdlManager as hdlManager
import autohdl.pkg_info as pkg_info
import autohdl.doc as doc
from autohdl.hdlGlobals import programmatorPath
import autohdl.programmator.programmator as prog
import sys

def main():
    parser = argparse.ArgumentParser(parents=[git.commands()], description='Helper to create designs')
    parser.add_argument('-doc', action='store_true', help='extended documentation in browser')
    parser.add_argument('-n', '--name', dest='name', default='',
        help='set design name and create structure (default name - current directory)')
    parser.add_argument('-v', '--version', dest='version', action='store_true', help='display package version')
    parser.add_argument('-tb', action='store_true', help='export project to active-hdl')
    parser.add_argument('-prog', action='store_true', help='run programmator')
    parser.add_argument('-edit', choices=['default_build', 'toolchain'], help='edit default build.yaml file')
    args = parser.parse_args()

    if args.prog:
        if os.path.basename(os.getcwd()) == 'script':
            if not os.path.exists(programmatorPath):
                os.mkdir(programmatorPath)
            os.chdir(programmatorPath)
        prog.run_another_proc()
        toolchain.Tool().get('ise_impact')
        sys.exit()

    if args.version:
        print 'autohdl version: ' + pkg_info.version()
    elif args.doc:
        doc.handler('index')
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
    #    dsn = structure.Design(iName = args.name)
        dsn = structure.generate(path=args.name)
        git.initialize(args.name if args.name else '.')
        print dsn


if __name__ == '__main__':
    main()

  
