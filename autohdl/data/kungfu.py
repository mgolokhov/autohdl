from autohdl import manager
# installation config (co)
# user config
# local project config (command line + this script)

cfg = {
    'technology': 'Spartan3e',
    'part': 'xc3s250e',
    'package': 'tq144',
    'speed_grade': '-5',
    'eeprom_bytes': '256',
    'src': [],
    'ignore_undefined_instances': [],
    'ucf': "",
    'sdc': "",
    'top_module': "",
    'include_path': "",
    # common stuff
    'webdav_src_path': 'git/hdl',
    'webdav_build_path': 'test/distout/rtl',
    'host': 'cs.scircus.ru',
    'webdav_files': [],
}

manager.kungfu(cfg=cfg)
