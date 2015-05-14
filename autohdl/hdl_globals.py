import os

FILE_CACHE = os.path.join(os.path.expanduser("~"), ".autohdl", "parsed_cache.json")
FILE_DEFAULT_CFG = os.path.join(os.path.expanduser("~"), ".autohdl", "kungfu_default.py")
FILE_USER_CFG = os.path.join(os.path.expanduser("~"), ".autohdl", "kungfu_user.py")


ignore_repo_dirs = ('.git', '.svn', '.hg',)
predefined_dirs = ('src', 'TestBench', 'resource', 'script',)
verilog_file_ext = ('.v', '.sv',)
vhdl_file_ext = ('.vhd', '.vhdl',)
NETLIST_EXT = ('.ngc',)

hdlFileExt = verilog_file_ext + vhdl_file_ext

autohdl_root = 'autohdl'
# start point directory is always dsn_name/script

SYNTHESIS_PATH = '../{}/synthesis'.format(autohdl_root)
IMPLEMENT_PATH = '../{}/implement'.format(autohdl_root)
