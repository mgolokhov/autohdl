import sqlite3


def incBuildVersion():
  aconnect = sqlite3.connect('autohdl/data/autohdl.db')
  acursor = aconnect.cursor()
  acursor.execute('''UPDATE version SET build = build + 1''')
  res = acursor.execute('''SELECT * FROM version''')
  version = res.fetchone()
  versionStr = '.'.join([str(i) for i in version])  
  aconnect.commit()
  aconnect.close()
  return versionStr


def getBuildVersion():
  aconnect = sqlite3.connect('autohdl/data/autohdl.db')
  acursor = aconnect.cursor()
  res = acursor.execute('''SELECT * FROM version''')
  version = res.fetchone()
  versionStr = '.'.join([str(i) for i in version])
  aconnect.commit()
  aconnect.close()
  return versionStr


def createAldecTable():
  aconnect = sqlite3.connect('data/autohdl.db')
  acursor = aconnect.cursor()
  
  
  acursor.execute('''
  SELECT name FROM sqlite_master WHERE type = 'table' and name = 'aldec'
  ''')
  
  if acursor.fetchone():
    print 'Dropping and creating new table.'
    acursor.execute('''DROP TABLE aldec''')
  
  
  
  acursor.execute('''
  CREATE TABLE aldec 
    (adf TEXT PRIMARY KEY, yaml TEXT, bydefault TEXT, preprocess TEXT)
    ''')
  
  ex = '''\
  INSERT INTO aldec 
    SELECT       'Files' as adf,              null as yaml,      null as bydefault,              'preprFiles' as preprocess
    UNION SELECT 'Settings.SYNTH_TOOL',       'synth_tool',      'MV_SYNPLIFY_PREMIER_C2009_06', null
    UNION SELECT 'Settings.IMPL_TOOL',        'impl_tool',       'MV_ISE111',                    null
    UNION SELECT 'Settings.FAMILY',           'family',          'Xilinx11x SPARTAN3E',          null
    UNION SELECT 'IMPLEMENTATION.FAMILY',     'family',          'Xilinx11x SPARTAN3E',          null
    UNION SELECT 'IMPLEMENTATION.DEVICE',     'device',          '3s1200efg320',                 null
    UNION SELECT 'IMPLEMENTATION.UCF',        'ucf',             '3s1200efg320',                 null
    UNION SELECT 'IMPLEMENTATION.OLD_FAMILY', 'family',          'Xilinx11x SPARTAN3E',          null
    UNION SELECT 'SYNTHESIS.TOPLEVEL',        'toplevel',        null,                           null
    UNION SELECT 'SYNTHESIS.FAMILY',          'family',          'Xilinx11x SPARTAN3E',          null
    UNION SELECT 'SYNTHESIS.OLD_FAMILY',      'family',          'Xilinx11x SPARTAN3E',          null
    UNION SELECT 'SYNTHESIS.DEVICE',          'device',          '3s1200efg320',                 null
    UNION SELECT 'SYNTHESIS.VERILOG_LANGUAGE','verilog_languge', 'SystemVerilog',                null
    UNION SELECT 'PHYS_SYNTHESIS.FAMILY',     'family',          'Xilinx11x SPARTAN3E',          null
    UNION SELECT 'PHYS_SYNTHESIS.DEVICE',     'device',          '3s1200efg320',                 null
    UNION SELECT 'LocalVerilogDirs',          'include_path',    '"."',                         'preprLocalVerilogDirs'
    UNION SELECT 'Files.Data',                 null,             null,                          'preprFilesData'
    
  '''
  acursor.execute(ex)
  
  print 'The total number of database rows that have been modified: ', aconnect.total_changes
  
  #ex = '''\
  #CREATE TABLE version
  #  (major INTEGER, minor INTEGER, build INTEGER PRIMARY KEY);
  #INSERT INTO version VALUES
  #  (2, 4, 1);
  #'''
  #for i in ex.split(';'):
  #  acursor.execute(i)
  
  aconnect.commit()
  aconnect.close()
  
if __name__ == '__main__':
  createAldecTable()
   