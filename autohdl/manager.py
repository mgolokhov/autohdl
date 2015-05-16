import argparse
import glob
import logging
import os
import pprint
import sys
import subprocess

# import cgitb
# cgitb.enable(format='text')

from autohdl import synplify
from autohdl import xilinx
from autohdl import configuration

alog = logging.getLogger(__name__)


def print_info(config):
    alog.info(('Main design settings:\n'
               + '#' * 40 +
               '\n'
               'technology : {technology}\n'
               'part       : {part}\n'
               'package    : {package}\n'
               'top module : {top}\n'
               'constraints: {ucf}\n'
               'eeprom size: {size} kilobytes\n'
               + '#' * 40 +
               '').format(technology=config.get('technology'),
                          part=config.get('part'),
                          package=config.get('package'),
                          top=config.get('top_module'),
                          ucf=config.get('constraints'),
                          size=config.get('eeprom_bytes'),
                          upload=config.get('upload')))


def cli_handler():
    parser = argparse.ArgumentParser(description='HDL Manager')
    parser.add_argument('-top', dest='top_module', help='set top module name')
    parser.add_argument('-synplify', nargs='?', const='batch', choices=['batch', 'gui'],
                        help='synthesis step [default=batch]')
    parser.add_argument('-xilinx', nargs='?', const='batch', choices=['batch', 'gui'],
                        help='implementation step [default=batch]')
    parser.add_argument('-mcs', nargs='?', help='generate .mcs from .bit file')
    parser.add_argument('-upload', action='store_true', help='upload firmware to WebDav server')
    parser.add_argument('-message', help='information about firmware')
    parser.add_argument('-debug', nargs='?', const='debug_all_modules')

    res = parser.parse_args()
    return res


def validate(cfg):
    # TODO: check constraints
    for k, s in (('top_module', 'Top module undefined'),):
        if not cfg.get(k):
            if 'batch' in (cfg.get('synplify'), cfg.get('xilinx'),):
                sys.exit('[Error] {}, exit...'.format(s))
            else:
                alog.warning("{}".format(s))


def set_debug(cfg):
    if cfg.get('debug') in ('debug_all_modules', __name__,):
        import logging.config as lc
        from autohdl import LOGGING_DICT
        LOGGING_DICT.update({"loggers": {"": {'handlers': ['cmd_debug', 'file_debug']}}})
        lc.dictConfig(LOGGING_DICT)


def kungfu(script_cfg):
    subprocess.call('hdl -v', shell=True)
    alog.info('Processing...')
    command_line_cfg = cli_handler()
    set_debug(vars(command_line_cfg))
    alog.debug('Command line args: ' + str(sys.argv))
    alog.debug(pprint.pformat(command_line_cfg))
    alog.debug('Script cfg:')
    alog.debug(pprint.pformat(script_cfg))
    configuration.copy()
    cfg = configuration.load(script_cfg=script_cfg, command_line_cfg=command_line_cfg)
    alog.debug('Merged cfg:')
    alog.debug(pprint.pformat(cfg))
    validate(cfg)

    # cfg['parsed'] = structure.parse(cfg['src'])
    print_info(cfg)

    # pprint.pprint(cfg)

    if len(sys.argv) == 1:
        cfg['synplify'] = 'batch'
        cfg['xilinx'] = 'batch'
        synplify.run(cfg)
        xilinx.run(cfg)
        if cfg.get('eeprom_kilobytes'):
            xilinx.bit_to_mcs(cfg)
        xilinx.copy_firmware(cfg)
    elif cfg.get('synplify'):
        synplify.run(cfg)
    elif cfg.get('xilinx'):
        xilinx.run(cfg)
        if cfg.get('eeprom_kilobytes'):
            xilinx.bit_to_mcs(cfg)
        xilinx.copy_firmware(cfg)
    elif cfg.get('mcs'):
        xilinx.bit_to_mcs(cfg)
        xilinx.copy_firmware(cfg)


if __name__ == '__main__':
    print('test')
