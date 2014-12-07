ignoreRepoDir = ['.git', '.svn']
predefDirs = ['src', 'TestBench', 'resource', 'script']
verilogFileExt = '.v .vei .veo .vl .vlb .vlg .vm .vmd .vo .vq .vqm .vt .sv'.split()
vhdlFileExt = '.vhd .vhdl .vhi .vhm .vhn .vho .vhq .vhs .tvhd .vht'.split()

hdlFileExt = verilogFileExt + vhdlFileExt

autohdlRoot = 'autohdl'
# start point directory is always dsn_name/script
buildFilePath = '../resource/build.yaml'
parsedCachePath = '../{}/parsed'.format(autohdlRoot)
aldecPath = '../{}/aldec'.format(autohdlRoot)
synthesisPath = '../{}/synthesis'.format(autohdlRoot)
implementPath = '../{}/implement'.format(autohdlRoot)
programmatorPath = '../{}/programmator'.format(autohdlRoot)