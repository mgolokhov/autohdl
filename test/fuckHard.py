'''
Creates couple of designs with interdependence.
Tries to pass all cycles (TestBench, synthesis, implement).
Compares with "gold" results.
Reports.
Cleans stuff.
'''
import os
import sys
import subprocess
import shutil

def fuckHard():
  '''
  Creates couple of designs with interdependence by calling hdl.py.
  
  Some calls as hdl.py <without name>, some hdl.py <name>.
  Generates valid verilog files (src and tb type).
  Generates valid build.xml files.
  Generates in some designs .ucf files.
  
  Runs TestBench (compare scripts in .tmp + logs)
  Runs synthesis (compare scripts in /script + logs)
  Runs implement (compare scripts in /script + logs)
  '''
  if not os.path.exists('functionalTests'):
#    shutil.rmtree('functionalTests')
    os.makedirs('functionalTests')
  os.chdir('functionalTests')
  
  pathHdlScript = sys.prefix+'/hdl.py'
  subprocess.call(['python', pathHdlScript, '-n', 'dsn1'])
  
  if not os.path.exists('dsn2'): os.makedirs('dsn2')
  os.chdir('dsn2')
  subprocess.call(['python', pathHdlScript])
  os.chdir('..')

  subprocess.call(['python', pathHdlScript, '-n', 'dsn3'])
  #
  # dsn1
  #
  f = open('dsn1/src/module1_1.v', 'w')
  f.write('''
  module module1_1 (input [5:0] in1_1, output out1_1);
  module2_1 inst2_1 (.in2_1a(in1_1[0]), .in2_1b(in1_1[1]), .out2_1(out2_1));
  module2_2 inst2_2 (.in2_2a(in1_1[2]), .in2_2b(in1_1[3]), .out2_2(out2_2));
  module3_1 inst3_1 (.in3_1a(in1_1[4]), .in3_1b(in1_1[5]), .out3_1(out3_1));
  module1_2 inst1_2 (.in1_2a(out2_1), .in1_2b(out2_2), .in1_2c(out3_1), .out1_2(out1_1));
  endmodule
  ''')
  f.close()
  f = open('dsn1/src/module1_2.v', 'w')
  f.write('''
  module module1_2 (input in1_2a, input in1_2b, input in1_2c, output out1_2);
  assign out1_2 = in1_2a + in1_2b + in1_2c;
  endmodule
  ''')
  f.close()
  f = open('dsn1/resource/build.xml', 'w')
  f.write('''
  <wsp>
   <dsn id="dsn1">
      <dep>dsn2/src</dep>
      <dep>dsn3/src/module3_1.v</dep>
   </dsn>
  </wsp>
  ''')
  f.close()
  
  #
  # dsn2
  #
  f = open('dsn2/src/module2_1.v', 'w')
  f.write('''
  module module2_1 (input in2_1a, input in2_1b, output out2_1);
  assign out2_1 = in2_1a + in2_1b;
  endmodule
  ''')
  f.close()
  
  f = open('dsn2/src/module2_2.v', 'w')
  f.write('''
  module module2_2 (input in2_2a, input in2_2b, output out2_2);
  assign out2_2 = in2_2a + in2_2b;
  endmodule
  ''')
  f.close()
  #
  # dsn3
  #
  f = open('dsn3/src/module3_1.v', 'w')
  f.write('''
  module module3_1 (input in3_1a, input in3_1b, output out3_1);
  assign out3_1 = in3_1a + in3_1b;
  endmodule
  ''')
  f.close()
  #
  #
  #
  f = open('dsn1/script/kungfu1.py', 'w')
  f.write('''
from autohdl.all import *
iTopModule = 'module1_1'
aldec.tb(iTopModule=iTopModule, iClean=True)
  ''')
  f.close()
    
  f = open('dsn1/script/kungfu2.py', 'w')
  f.write('''
from autohdl.all import *
iTopModule = 'module1_1'
synthesis.run(iTopModule=iTopModule)
  ''')
  f.close()

  os.chdir('dsn1/script')
  subprocess.Popen(['python', 'kungfu1.py'])
  subprocess.Popen(['python', 'kungfu2.py'])
  print 'sucks'

