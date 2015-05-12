ignore_repo_dirs = ['.git', '.svn', '.hg']
predefined_dirs = ['src', 'TestBench', 'resource', 'script']
verilog_file_ext = '.v .vei .veo .vl .vlb .vlg .vm .vmd .vo .vq .vqm .vt .sv'.split()
vhdl_file_ext = '.vhd .vhdl .vhi .vhm .vhn .vho .vhq .vhs .tvhd .vht'.split()

hdlFileExt = verilog_file_ext + vhdl_file_ext

autohdl_root = 'autohdl'
# start point directory is always dsn_name/script
buildFilePath = '../resource/build.yaml'
parsedCachePath = '../{}/parsed'.format(autohdl_root)
aldecPath = '../{}/aldec'.format(autohdl_root)
synthesisPath = '../{}/synthesis'.format(autohdl_root)
implementPath = '../{}/implement'.format(autohdl_root)
