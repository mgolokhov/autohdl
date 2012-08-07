ignoreRepoDir = ['.git', '.svn']
predefDirs = ['src', 'TestBench', 'resource', 'script']
verilogFileExt = '.v .vei .veo .vl .vlb .vlg .vm .vmd .vo .vq .vqm .vt'.split()
vhdlFileExt = '.vhd .vhdl .vhi .vhm .vhn .vho .vhq .vhs .tvhd .vht'.split()

hdlFileExt = verilogFileExt + vhdlFileExt

# start point directory is always dsn_name/script
buildFilePath = '../resource/build.yaml'
parsedCachePath = '../.hdl/parsed'
aldecPath = '../.hdl/aldec'
synthesisPath = '../.hdl/synthesis'
implementPath = '../.hdl/implement'