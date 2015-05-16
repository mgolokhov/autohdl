import logging.config as lc
import os

_AUTOHDL_CONFIG_DIR_ = os.path.join(os.path.expanduser("~"), ".autohdl")
FILE_CACHE = os.path.join(_AUTOHDL_CONFIG_DIR_, "parsed_cache.json")
FILE_DEFAULT_CFG = os.path.join(_AUTOHDL_CONFIG_DIR_, "kungfu_default.py")
FILE_USER_CFG = os.path.join(_AUTOHDL_CONFIG_DIR_, "kungfu_user.py")
FILE_TOOLCHAIN_CFG = os.path.join(_AUTOHDL_CONFIG_DIR_, 'toolchain.json')


IGNORE_REPO_DIRS = ('.git', '.svn', '.hg',)
PREDEFINED_DIRS = ('src', 'TestBench', 'resource', 'script',)
VERILOG_FILE_EXT = ('.v', '.sv',)
VHDL_FILE_EXT = ('.vhd', '.vhdl',)
NETLIST_EXT = ('.ngc',)

VERILOG_VHDL_FILE_EXT = VERILOG_FILE_EXT + VHDL_FILE_EXT

AUTOHDL_ROOT = 'autohdl'
# start point directory is always dsn_name/script

SYNTHESIS_PATH = '../{}/synthesis'.format(AUTOHDL_ROOT)
IMPLEMENT_PATH = '../{}/implement'.format(AUTOHDL_ROOT)

FILE_LOGGING = os.path.join(os.path.expanduser("~"), ".autohdl", "logging.txt")

LOGGING_DICT = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s:%(filename)s:%(lineno)d:%(levelname)s:\n%(message)s'
        },
        'simple': {
            'format': '%(levelname)s: %(message)s'
        },
    },
    'handlers': {
        'cmd_debug': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'verbose'
        },
        'cmd_info': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'simple'
        },
        'file_debug': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            "formatter": "simple",
            "filename": FILE_LOGGING,
            "maxBytes": 2000000,
            "backupCount": 1,
            "encoding": "utf8",
        }
    },
    ''
    'loggers': {
        '': {
            'handlers': ['cmd_info', 'file_debug'],
            'level': 'DEBUG',
        },
    }
}

lc.dictConfig(LOGGING_DICT)

