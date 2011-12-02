ignore = ['\.git', '\.svn']
ignoreRepoFiles = ['\.git', '\.svn']
predefDirs = ['src', 'TestBench', 'resource', 'script']
verilogFileExt = 'v;vei;veo;vl;vlb;vlg;vm;vmd;vo;vq;vqm;vt'.split(';')
verilogFileExtRe = ['\.'+i+'$' for i in verilogFileExt]
vhdlFileExt = 'vhd;vhdl;vhi;vhm;vhn;vho;vhq;vhs;tvhd;vht'.split(';')
vhdlFileExtRe = ['\.'+i+'$' for i in vhdlFileExt]
srcFileTypes = ['.v', '.sv', '.vhd', '.vhdl']