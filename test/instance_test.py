import sys, os, shutil
import unittest
sys.path.append('..')
from instance import *

from hdlLogger import *
#log.setLevel(logging.DEBUG)


class Test(unittest.TestCase):
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
    expected = {'add1': ['inst1', 'inst2', 'inst4', 'inst5', 'inst3', 'inst4', 'inst6']}
    self.assertDictEqual(expected, getInstances(t))


  def test_parseFiles(self):
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

    module add2(
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
    
    pathCur = os.getcwd().replace('\\', '/')
    
    pathF1 = pathCur+'/f1'
    f = open(pathF1, 'w')
    f.write(t)
    f.close()
    
    pathF2 = pathCur+'/f2'
    f = open(pathF2, 'w')
    f.write(t)
    f.close()
    expected = {'add1': ['G:/repo/git/autohdl/test/f1',
                        'inst1', 'inst2', 'inst4', 'inst5', 'inst3', 'inst4', 'inst6'],
                'add2': ['G:/repo/git/autohdl/test/f1',
                         'inst1', 'inst2', 'inst4', 'inst5', 'inst3', 'inst4', 'inst6'],
                'add1': ['G:/repo/git/autohdl/test/f2',
                        'inst1', 'inst2', 'inst4', 'inst5', 'inst3', 'inst4', 'inst6'],
                'add2': ['G:/repo/git/autohdl/test/f2',
                         'inst1', 'inst2', 'inst4', 'inst5', 'inst3', 'inst4', 'inst6']}
    self.assertDictEqual(expected, parseFiles([pathF1, pathF2]))
    os.remove(pathF1)
    os.remove(pathF2)

  def test_undefFirstCall(self):
    t = '''
    module add1(
    input a,
    output b);
    assign b = a;
    inst1 name (d,f);
    endmodule

    module add2(
    input a,
    output b);
    assign b = a;
    inst2 name(d,f);
    endmodule
    '''
    t2 = '''
    module inst1 (input a, output b);
    endmodule
    '''
    pathCur = os.getcwd().replace('\\', '/')
    
    pathF3 = pathCur+'/f3'
    f = open(pathF3, 'w')
    f.write(t)
    f.close()
    
    pathF4 = pathCur+'/f4'
    f = open(pathF4, 'w')
    f.write(t2)
    f.close()
    
    expectedParsed = {'inst1': ['G:/repo/git/autohdl/test/f4'],
                      'add1': ['G:/repo/git/autohdl/test/f3', 'inst1'],
                      'add2': ['G:/repo/git/autohdl/test/f3', 'inst2']
                      }
    expectedUndef = set([('G:/repo/git/autohdl/test/f3', 'inst2')])
    parsed, undef = undefFirstCall([pathF3, pathF4])
    self.assertDictEqual(expectedParsed, parsed)
    self.assertSetEqual(expectedUndef, undef)
    os.remove(pathF3)
    os.remove(pathF4)
    
    
  def test_getUndef(self):
    t = '''
    module add1(
    input a,
    output b);
    assign b = a;
    inst1 name (d,f);
    endmodule

    module add2(
    input a,
    output b);
    assign b = a;
    inst2 name(d,f);
    endmodule
    '''
    t2 = '''
    module inst1 (input a, output b);
    endmodule
    '''
    pathCur = os.getcwd().replace('\\', '/')
    
    pathF5 = pathCur+'/f5'
    f = open(pathF5, 'w')
    f.write(t)
    f.close()
    
    pathF6 = pathCur+'/f6'
    f = open(pathF6, 'w')
    f.write(t2)
    f.close()    
    
    t3 = '''
    module inst2 (input a, output b);
    inst3 name1(a,b);
    inst4 name2(c,d);
    inst3 name3(e,f);
    endmodule
    '''
    
    pathF7 = pathCur+'/f7'
    f = open(pathF7, 'w')
    f.write(t3)
    f.close() 
#    log.setLevel(logging.DEBUG)
    parsed, undef = undefFirstCall([pathF5, pathF6])
    
    parsed, undef = getUndef(iFiles = [pathF7],
                             iParsed = parsed,
                             iUndefInstances = undef)
    expectedParsed = {'add1': ['G:/repo/git/autohdl/test/f5', 'inst1'],
                      'add2': ['G:/repo/git/autohdl/test/f5', 'inst2'],
                      'inst1': ['G:/repo/git/autohdl/test/f6'],
                      'inst2': ['G:/repo/git/autohdl/test/f7', 'inst3', 'inst4', 'inst3']}
    self.maxDiff = None
    self.assertDictEqual(expectedParsed, parsed)
    expectedUndef = set([(pathF7, 'inst3'), (pathF7, 'inst4')])
    self.assertSetEqual(expectedUndef, undef)
    os.remove(pathF5)
    os.remove(pathF6)
    os.remove(pathF7)
    
if __name__ == '__main__':
  unittest.main()
#  tests = ['test_removeComments'
#           ]
#
#  suite = unittest.TestSuite(map(Test, tests))
#  unittest.TextTestRunner(verbosity=2).run(suite)
  