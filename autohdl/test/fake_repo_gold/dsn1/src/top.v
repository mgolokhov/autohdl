// test 1
`include "include.vh"
module top(
input a,
input b,
output c
);

inst1 inst1_e(a, b);
inst2 #(param1, param2)inst2_e(a, b);
inst3 #(.param1(param1))inst3_e(a,b);
`ifdef test1
inst4 #(
.param(param), .param2(10)
)
inst4_e
(.a(a),
b(b));
`elsif test2
inst5 inst5_e(a, b);
`else
inst6 inst6_e(a, b,
 c); 
`endif


endmodule



