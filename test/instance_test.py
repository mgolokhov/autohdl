import sys, os, shutil
import unittest
sys.path.append('..')
from instance import *

from hdlLogger import *
#log.setLevel(logging.DEBUG)


class Test(unittest.TestCase):
  def setUp(self):
    if not os.path.exists('tmp_test_dir'):
      os.mkdir('tmp_test_dir')
  
  def tearDown(self):
    if os.path.exists('tmp_test_dir'):
      shutil.rmtree('tmp_test_dir')
  
  def test_removeComments(self):
    t = '''
    that one is fake "certainly//"? // but me
    first comment
    /*comment*/
    second
    //comment
    ///comment
    /*//*/
    big comment
    /*comment
    comment*/
    that one is fake "certainly//"?
    may and that one "nope" //comment
    multi fake "/*not me*/"
    '''
    expected = '''
    that one is fake "certainly//"? 
    first comment
    
    second
    
    
    
    big comment
    
    that one is fake "certainly//"?
    may and that one "nope" 
    multi fake "/*not me*/"
    '''   
    self.assertMultiLineEqual(expected, removeComments(t)) 
    
    t = '''\
module ctrl_v2_kiortest
    (
    // Global Inputs
    
    input  clk_in,  // Clock 50 Mhz
    input  rst_in, // Reset Active High
    
    // LITTLE-USB Serial Interface
    
    input  usb_rx_in,  // LITLE_USB Receiver
    output  usb_tx_out,  // LITTLE_USB Tranceiver
    
    // SWITCH BOX 
    
    input  [1:0]  box_in, // Box input signals
    output  [1:0]  box_out,// Box multiplexers signals    
    '''
    expected = '''\
module ctrl_v2_kiortest
    (
    
    
    input  clk_in,  
    input  rst_in, 
    
    
    
    input  usb_rx_in,  
    output  usb_tx_out,  
    
    
    
    input  [1:0]  box_in, 
    output  [1:0]  box_out,
    '''
    self.assertMultiLineEqual(expected, removeComments(t))
    
  def test_removeFunc(self):
    t = '''
    module simple_function();
    
    function  myfunction;
    input a, b, c, d;
    begin
      myfunction = ((a+b) + (c-d));
    end
    endfunction
    
    endmodule


    module fact;
    function [7:0] getbyte;
    input [15:0] address;
    reg [3:0] result_expression;
    begin

    getbyte = result_expression;
    end
    endfunction
    
    one_more_func
    function integer log2(input integer value);
        begin
            value = value-1;
            for (log2=0; value>0; log2=log2+1)
                value = value>>1;
        end
    endfunction
    and_more
    function reg parity (input integer arg);
        begin
            if (arg)
                parity = (^buffer[pBufferWidth-2:0] == buffer[pBufferWidth-1]);
            else
                parity = 1;
        end
    endfunction
    endmodule
    '''
    
    expected = '''
    module simple_function();
    
       
    endmodule


    module fact;
       
    one_more_func
       and_more
       endmodule
    '''
    
    self.assertMultiLineEqual(expected, removeFunc(t))

    
  def test_getInstances(self):
    t = '''
    module add1(
    input a,
    output b);
    assign b = a;
    inst1 nameInst(d,f);
    inst2 nameInst(d,f);
    endmodule
    '''
    expected = {'add1': ['inst1', 'inst2']}
    self.assertDictEqual(expected, getInstances(t))

    t = '''module name();
    module2_1 inst2_1 (.in2_1a(in1_1[0]), .in2_1b(in1_1[1]), .out2_1(out2_1));
    module2_2 inst2_1 (
    .in2_1a(in1_1[0]),
     .in2_1b(in1_1[1]), 
     .out2_1(out2_1)
     );
    endmodule
    '''
    expected = {'name':['module2_1', 'module2_2']}
    self.assertDictEqual(expected, getInstances(t))


    t = '''
    module add1(
    input a,
    output b);
    assign b = a;
    inst1 nameInst(d,f);
    inst2  nameInst  (  d , f ) ;
    inst4 name (.i1(i1), .i2(i2));
    inst5 name (
    .i1(i1),
     .i2(i2)
     );
    inst3  nameInst  (
    d,
    f);
    inst4 #(p1, p2) name (i1, i2); 
    inst6 #(
    .p1(p1), 
    .p1(p2))name(
    .i1(i1), 
    .i2(i2)); 
    endmodule
    '''
    expected = {'add1': ['inst1', 'inst2', 'inst4', 'inst5', 'inst3', 'inst6']}
    self.assertDictEqual(expected, getInstances(t))


  def test_parseFiles(self):
      pathCur = os.getcwd().replace('\\', '/')+'/tmp_test_dir'
      f2 = '''
      module inst1 (input a, output b);
      endmodule
      '''
      path_f2 = pathCur+'/f2'
      f = open(path_f2, 'w')
      f.write(f2)
      f.close()
      expectedParsed = {'inst1': [path_f2]}
      
      f3 = '''
      module inst2 (input a, output b);
      inst3 name1(a,b);
      inst4 name2(c,d);
      inst3 name3(e,f);
      endmodule
      '''
      path_f3 = pathCur+'/f3'
      f = open(path_f3, 'w')
      f.write(f3)
      f.close() 
      expectedParsed.update({'inst2': [path_f3, 'inst3', 'inst4']})
            
      parsed = parseFiles([path_f2, 'fake_path', path_f3])
      self.assertDictEqual(expectedParsed, parsed)
      
  def test_instTreeDep(self):
    parsed = {'top':['path_top', 'inst1', 'inst2'],
              'inst3': ['path_inst3', 'inst1'],
              'inst1': ['path_inst1', 'inst11']
              }
    top = {'top':['path_top', 'inst1', 'inst2']}
    
    expectedDep = [{'top': ['path_top', 'inst1', 'inst2']},
                   {'inst1': ['path_inst1', 'inst11']}
                  ]
    expectedUndef = {'inst11':'path_inst1',
                     'inst2':'path_top'
                    }
    dep, undef = instTreeDep(iTop = top, iSrc = parsed)
    self.assertListEqual(expectedDep, dep)
    self.assertDictEqual(expectedUndef, undef)
  
  def test_analyze(self):
      pathCur = os.getcwd().replace('\\', '/')+'/tmp_test_dir'
  
      f1 = '''
      module add1(input a,output b);
      inst1 name (d,f);
      endmodule
  
      module add2(input a,output b);
      inst2 name(d,f);
      endmodule
      '''
      path_f1 = pathCur+'/f1'
      f = open(path_f1, 'w')
      f.write(f1)
      f.close()
      expectedParsed = {'add1': [path_f1, 'inst1'],
                        'add2': [path_f1, 'inst2']
                        }
      
      f2 = '''
      module inst1 (input a, output b);
      endmodule
      '''
      path_f2 = pathCur+'/f2'
      f = open(path_f2, 'w')
      f.write(f2)
      f.close()
      expectedParsed.update({'inst1': [path_f2]})
                          
      
      f3 = '''
      module inst2 (input a, output b);
      inst3 name1(a,b);
      inst4 name2(c,d);
      inst3 name3(e,f);
      endmodule
      '''
      path_f3 = pathCur+'/f3'
      f = open(path_f3, 'w')
      f.write(f3)
      f.close() 
      expectedParsed.update({'inst2': [path_f3, 'inst3', 'inst4']})
  
      expectedUndef = {'inst3':path_f3, 'inst4':path_f3}

      parsed = {}
      undef = analyze(iPathFiles = [path_f1, path_f2, path_f3],
                      ioParsed = parsed)
      #
      # test first call
      #
      self.assertDictEqual(expectedParsed, parsed)
      self.assertDictEqual(expectedUndef, undef)
      #
      # test next call
      #
      f4 = '''
      module inst4 (input a, output b);
      inst41 name2(c,d);
      endmodule
      '''
      path_f4 = pathCur+'/f4'
      f = open(path_f4, 'w')
      f.write(f4)
      f.close() 
      expectedParsed.update({'inst4': [path_f4, 'inst41']})

      undef = analyze(iPathFiles = [path_f4],
                      ioParsed = parsed,
                      iUndefInst = undef)
      expectedUndef = {'inst3':path_f3, 'inst41':path_f4}
      self.assertDictEqual(expectedParsed, parsed)
      self.assertDictEqual(expectedUndef, undef)
      #
      # one more call
      #
      f5 = '''
      module inst41 (input a, output b);
      endmodule
      '''
      path_f5 = pathCur+'/f5'
      f = open(path_f5, 'w')
      f.write(f5)
      f.close() 
      expectedParsed.update({'inst41': [path_f5]})

      f6 = '''
      module inst3 (input a, output b);
      inst33 name33(a,b);
      endmodule
      module inst33 (input a, output b);
      endmodule
      '''
      path_f6 = pathCur+'/f6'
      f = open(path_f6, 'w')
      f.write(f6)
      f.close() 
      expectedParsed.update({'inst3': [path_f6, 'inst33'], 'inst33': [path_f6]})

      # should be ignored 
      f7 = '''
      module inst666 (input a, output b);
      inst666_1 name666_1(a,b);
      endmodule
      '''
      path_f7 = pathCur+'/f7'
      f = open(path_f7, 'w')
      f.write(f7)
      f.close()

      undef = analyze(iPathFiles = [path_f5, path_f6, path_f7],
                      ioParsed = parsed,
                      iUndefInst = undef)
      expectedUndef = {}
      self.assertDictEqual(expectedParsed, parsed)
      self.assertDictEqual(expectedUndef, undef)

    
if __name__ == '__main__':
#  unittest.main()
  tests = [
           'test_removeComments',
           'test_removeFunc',
           'test_getInstances',
           'test_parseFiles',
           'test_instTreeDep',
           'test_analyze'
           ]

  suite = unittest.TestSuite(map(Test, tests))
  unittest.TextTestRunner(verbosity=2).run(suite)
  