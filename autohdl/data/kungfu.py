from autohdl import manager
# installation config (reference staff)
# user config
# local project config (command line + this script)

cfg = {
    'technology': 'Spartan3e',
    'part': 'xc3s250e',
    'package': 'tq144',
    'speed_grade': '-5',
    'eeprom_kilobytes': '256',
    'src': [],
    'ignore_undefined_instances': [],
    'top_module': "",
    'include_paths': [],
}

if __name__ == '__main__':
    manager.kungfu(script_cfg=cfg)
