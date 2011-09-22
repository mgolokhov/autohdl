`default_nettype none
//
//		Module:		isa_top
//		Version:	0.1
//		Project:	cd_isa
//		FPGA:		Xilinx Spartan3S200 tq144
//  	Board:		hw_isa
//		Author:		Serge V. Kior
//		Testbench:	-none-
//		Repositary:	http://dev.sign4tech.com/svn/SCIRCUS/hdl/cd_isa/
//		Wiki:		http://dev.sign4tech.com:8080/confluence/display/SCVAM/isa_top
//


module cd_isa (
	input			clk_in,				//p55 ���� �������� ������� 	������� 	 
 	input			rst_in_,			//p12 j1-14 -> p58 j2-24 ���� ������ 	������ 	
	//
	// RS485_xxx5
	//
	output			rs_tx_out,			//p124 j2-22 isa2hi ����� ����. ����������
	input			rs_rx_in,			//p125 -> p55 j2-23 hi2isa ���� ����� ����������
	input			rs_rx2_in,			//p65 -> p127 j2-24 RS485_INB5 ����� ������ ��������� ����� ����� 5
	
	output			rs_tx_0_out,		//p108 j2-6 ����� � ��1 
	output			rs_tx_1_out,		//p103 j2-10 ����� � ��2
	output			rs_tx_2_out,		//p98 j2-14 ����� � ��3 
	output			rs_tx_3_out,		//p118 j2-18 ����� � ��4 
	
	input			rs_rx_0a_in,		//p107 -> p104 j2-7 ���� �� ��1 � 
	input			rs_rx_0b_in,		//p105 j2-8 ���� �� ��1 b
	input			rs_rx_1a_in,		//p102 -> p99 j2-11 ���� �� ��2 � 
	input			rs_rx_1b_in,		//p100 j2-12 ���� �� ��2 b
	input			rs_rx_2a_in,		//p112 -> p116 j2-15 ���� �� ��3 � 
	input			rs_rx_2b_in,		//p113 j2-16 ���� �� ��3 b
	input			rs_rx_3a_in,		//p119 ->p123 j2-19 ���� �� ��4 � 
	input			rs_rx_3b_in,		//p122 j2-20 ���� �� ��4 b
	inout	[7:0]	isa_data_io,		//��������������� ���������  ������ ISA
	//2b  p7	 j1-10
	//4b  p5	 j1-8
	//6b  p2	 j1-6
	//7b  p1	 j1-5
	//5b  p4	 j1-7
	//3b  p6	 j1-9
	//1b  p8	 j1-11
	//0b p10     j1-12
	output			isa_tr_data_out,	//p11 j1-13 ������� ����������� ������� �������
	input			isa_aen_in,			//p13 j1-15 -> p131 j1-24 ������ ���������� ������ ISA 
	input	[9:0]	isa_addr_in, 		//���� ������ ISA
	//9 p141	-> p12 j1-14 
	//8 p140	-> p13 j1-15
	//7 p137	-> p14 j1-16
	//6 p132	-> p15 j1-17
	//5 p135	-> p141 j1-18
	//4 p130	-> p140 j1-19
	//3 p131	-> p137 j1-20
	//2 p128	-> p132 j1-21
	//1 p129	-> p135 j1-22
	//0 p58		-> p130 j1-23
	input			isa_iow_in,			//p14 j1-16 -> p128 j1-25 ������ � ���� �� ISA 
	input			isa_ior_in,			//p15 -> p129 j1-26 ������ �� ����� �� ISA 
	//
	// not yet
	//
	output rs_tx_0_out_en, //p104 -> p107 j2-5 ���������� �������� �� ������ 1
	output rs_tx_1_out_en, //p99 -> p102 j2-9 ���������� �������� �� ������ 2
	output rs_tx_2_out_en, //p116 -> p112 j2-13 ���������� �������� �� ������ 3
	output rs_tx_3_out_en, //p123 -> p119 j2-17 ���������� �������� �� ������ 4
	output rs_tx_out_en	   //p127 -> p125 j2-21 ���������� �������� �� ������ ISA2HI
	);
	
	assign rs_tx_0_out_en = 1; 
	assign rs_tx_1_out_en = 1;
	assign rs_tx_2_out_en = 1;
	assign rs_tx_3_out_en = 1;
	assign rs_tx_out_en = 1;
	
	
// ���� ������

wire	[13:0]	leds;			//���������� �� ���
wire	[13:0]	keys;			//������� �� ���
wire	[11:0]	ai0;			//�������� ������������� ��1 
wire	[11:0]	ai1;			//�������� ������������� ��2
wire	[11:0]	ai2;			//�������� ������������� ��3 
wire	[11:0]	ai3;			//�������� ������������� ��4 
wire	[11:0]	ai4;			//�������� ������������� ��
wire	[15:0]	pdu_0_status;	// 	 ���������� ��� ��1
wire	[15:0]	pdu_1_status;	// 	 ���������� ��� ��2
wire	[15:0]	pdu_2_status;	// 	 ���������� ��� ��3
wire	[15:0]	pdu_3_status;	// 	 ���������� ��� ��4
wire	[31:0]	sensor0;		// 	 �������� ������� ��1
wire	[15:0]	ca0_stat;		//	 ��������� ��������������� ��1
wire	[31:0]	sensor1;		// 	 �������� ������� ��2
wire	[15:0]	ca1_stat;		//	 ��������� ��������������� ��2
wire	[31:0]	sensor2;		// 	 �������� ������� ��3
wire	[15:0]	ca2_stat;		//	 ��������� ��������������� ��3
wire	[31:0]	sensor3;		// 	 �������� ������� ��4
wire	[15:0]	ca3_stat;		//	 ��������� ��������������� ��4
wire			f100;			//������ 100 ��
wire	[13:0]	man_leds;		//������ �� ���������� �� ������� ���������� 
wire	[15:0]	man_pdu_0;		// 	 ���������� ��� ��1 �� ������� ���������� 
wire	[15:0]	man_pdu_1;		// 	 ���������� ��� ��2 �� ������� ���������� 
wire	[15:0]	man_pdu_2;		// 	 ���������� ��� ��3 �� ������� ���������� 
wire	[15:0]	man_pdu_3;		// 	 ���������� ��� ��4 �� ������� ���������� 
wire	selector;				//	������������ ����� ������ � �������������� �������
wire	[13:0]	isa_leds;		//������ �� ���������� �� ���������� 
wire	[15:0]	isa_pdu_0;		// 	 ���������� ��� ��1 �� ����������
wire	[15:0]	isa_pdu_1;		// 	 ���������� ��� ��2 �� ����������
wire	[15:0]	isa_pdu_2;		// 	 ���������� ��� ��3 �� ����������
wire	[15:0]	isa_pdu_3;		// 	 ���������� ��� ��4 �� ����������


assign selector = 0;

wire rst_in;
assign rst_in = rst_in_;
//
// not yet
//
if_pdu2hi_tx pdu2hi_tx (
    .clk_in(clk_in),
	.rst_in(rst_in),
	.rs_tx_out(rs_tx_out),
	.leds_in(leds),
	.f100_in(f100)
); 
//assign isa_data_io = rs_tx_out;
//
// should be (minimum)----------------------
//
if_hi2pdu_rx hi2pdu_rx  (
    .clk_in(clk_in),
	.rst_in(rst_in),
	.rs_rx_in(rs_rx_in),
	.keys_out(keys),
	.ai0_out(ai0),
	.ai1_out(ai1),
	.ai2_out(ai2),
	.ai3_out(ai3),
	.ai4_out(ai4)
);	  

if_pdu2ctrl_tx pdu2ctrl_tx_1  (
	.clk_in(clk_in),
	.rst_in(rst_in),
	.pdu_in(pdu_0_status),
	.rs_tx_out(rs_tx_0_out ),
	.f100_in(f100)
);

if_pdu2ctrl_tx pdu2ctrl_tx_2  (
	.clk_in(clk_in),
	.rst_in(rst_in),
	.pdu_in(pdu_1_status),
	.rs_tx_out(rs_tx_1_out ),
	.f100_in(f100)
);

if_pdu2ctrl_tx pdu2ctrl_tx_3  (
	.clk_in(clk_in),
	.rst_in(rst_in),
	.pdu_in(pdu_2_status),
	.rs_tx_out(rs_tx_2_out ),
	.f100_in(f100)
);

if_pdu2ctrl_tx pdu2ctrl_tx_4  (
	.clk_in(clk_in),
	.rst_in(rst_in),
	.pdu_in(pdu_3_status),
	.rs_tx_out(rs_tx_3_out ),
	.f100_in(f100)
);	  
//
//-------------------------------------------------
//
wire ctrl_rx_a_active_out0;
wire ctrl_rx_b_active_out0;
wire rs_a_active_out0;
wire rs_b_active_out0;
wire stf_out0;
wire str_out0;
wire stop_out0;
wire [1:0] mpu_0_status;

if_ctrl2pdu_rx ctrl2pdu_rx_0
(.clk_in(clk_in),
	.rst_in(rst_in),
	.rs_rx_a_in(rs_rx_0a_in),
	.rs_rx_b_in(rs_rx_0b_in),
	.mpu_status_out(mpu_0_status),
	.enc_out(sensor0),
	.ctrl_rx_a_active_out(ctrl_rx_a_active_out0),
	.ctrl_rx_b_active_out(ctrl_rx_b_active_out0),
	.stf_out(stf_out0),
	.str_out(str_out0),
	.stop_out(stop_out0),
	.ka_status_out(ca0_stat),
	.rs_a_active_out(rs_a_active_out0),
	.rs_b_active_out(rs_b_active_out0)
);

wire ctrl_rx_a_active_out1;
wire ctrl_rx_b_active_out1;
wire rs_a_active_out1;
wire rs_b_active_out1;
wire stf_out1;
wire str_out1;
wire stop_out1;
wire [1:0] mpu_1_status;

if_ctrl2pdu_rx ctrl2pdu_rx_1
(.clk_in(clk_in),
	.rst_in(rst_in),
	.rs_rx_a_in(rs_rx_1a_in),
	.rs_rx_b_in(rs_rx_1b_in),
	.mpu_status_out(mpu_1_status),
	.enc_out(sensor1),
	.ctrl_rx_a_active_out(ctrl_rx_a_active_out1),
	.ctrl_rx_b_active_out(ctrl_rx_b_active_out1),
	.stf_out(stf_out1),
	.str_out(str_out1),
	.stop_out(stop_out1),
	.ka_status_out(ca1_stat),
	.rs_a_active_out(rs_a_active_out1),
	.rs_b_active_out(rs_b_active_out1)
);
wire ctrl_rx_a_active_out2;
wire ctrl_rx_b_active_out2;
wire rs_a_active_out2;
wire rs_b_active_out2;
wire stf_out2;
wire str_out2;
wire stop_out2;
wire [1:0] mpu_2_status;

if_ctrl2pdu_rx ctrl2pdu_rx_2
(.clk_in(clk_in),
	.rst_in(rst_in),
	.rs_rx_a_in(rs_rx_2a_in),
	.rs_rx_b_in(rs_rx_2b_in),
	.mpu_status_out(mpu_2_status),
	.enc_out(sensor2),
	.ctrl_rx_a_active_out(ctrl_rx_a_active_out2),
	.ctrl_rx_b_active_out(ctrl_rx_b_active_out2),
	.stf_out(stf_out2),
	.str_out(str_out2),
	.stop_out(stop_out2),
	.ka_status_out(ca2_stat),
	.rs_a_active_out(rs_a_active_out2),
	.rs_b_active_out(rs_b_active_out2)
);
wire ctrl_rx_a_active_out3;
wire ctrl_rx_b_active_out3;
wire rs_a_active_out3;
wire rs_b_active_out3;
wire stf_out3;
wire str_out3;
wire stop_out3;
wire [1:0] mpu_3_status;

if_ctrl2pdu_rx ctrl2pdu_rx_3
(.clk_in(clk_in),
	.rst_in(rst_in),
	.rs_rx_a_in(rs_rx_3a_in),
	.rs_rx_b_in(rs_rx_3b_in),
	.mpu_status_out(mpu_3_status),
	.enc_out(sensor3),
	.ctrl_rx_a_active_out(ctrl_rx_a_active_out3),
	.ctrl_rx_b_active_out(ctrl_rx_b_active_out3),
	.stf_out(stf_out3),
	.str_out(str_out3),
	.stop_out(stop_out3),
	.ka_status_out(ca3_stat),
	.rs_a_active_out(rs_a_active_out3),
	.rs_b_active_out(rs_b_active_out3)
);

/////BUG: Temporary because if_ctrl2pdu_rx is not awailable
//if_ctrl2pdu_rx ctrl2pdu_rx_1(
//	.clk_in(clk_in),
//	.rst_in(rst_in),
//	.rs_rx_in(rs_rx_0a_in ),
//	.enc_out(sensor0),
//	.ka_status_out(ca0_stat)
//);


f100_generator f100_gen (
    .clk_in(clk_in),
	.rst_in(rst_in),
	.f100_out(f100)
);	

manual_ctrl manual_ctrl (
    .clk_in(clk_in),
	.rst_in(rst_in),
	.keys_in(keys),
	.ca0_stat_in(ca0_stat),
	.ca1_stat_in(ca1_stat),
	.ca2_stat_in(ca2_stat),
	.ca3_stat_in(ca3_stat),
	.leds_out(man_leds),
	.ai0_in(ai0),
	.ai1_in(ai1),
	.ai2_in(ai2),
	.ai3_in(ai3),
	.ai4_in(ai4),
	.f100_in(f100),
	.pdu_0_status_out(man_pdu_0),
	.pdu_1_status_out(man_pdu_1),
	.pdu_2_status_out(man_pdu_2),
	.pdu_3_status_out(man_pdu_3)
);	

isa_vs_manual_selector Label1 (.clk_in(clk_in),
	.rst_in(rst_in),
	.selector_in(selector),
	.man_leds_in(man_leds),
	.man_pdu_0_status_in(man_pdu_0),
	.man_pdu_1_status_in(man_pdu_1),
	.man_pdu_2_status_in(man_pdu_2),
	.man_pdu_3_status_in(man_pdu_3),
	.isa_leds_in(isa_leds),
	.isa_pdu_0_status_in(isa_pdu_0),
	.isa_pdu_1_status_in(isa_pdu_1),
	.isa_pdu_2_status_in(isa_pdu_2),
	.isa_pdu_3_status_in(isa_pdu_3),
	.leds_out(leds),
	.pdu_0_status_out(pdu_0_status),
	.pdu_1_status_out(pdu_1_status),
	.pdu_2_status_out(pdu_2_status),
	.pdu_3_status_out(pdu_3_status)
);
//assign isa_tr_data_out = 0;
//wire isa_tr_data_out_;
if_isa isa (
	.clk_in(clk_in),
	.rst_in(rst_in),
	.isa_data_io(isa_data_io),
	.isa_tr_data_out(isa_tr_data_out),
	.isa_aen_in(isa_aen_in),
	.isa_addr_in(isa_addr_in),
	.isa_iow_in(isa_iow_in),
	.isa_ior_in(isa_ior_in),
	.pdu_0_status_out(isa_pdu_0),
	.pdu_1_status_out(isa_pdu_1),
	.pdu_2_status_out(isa_pdu_2),
	.pdu_3_status_out(isa_pdu_3),
	.leds_out(isa_leds),
	.keys_in(14'h3AAA/*keys*/),
	.ca0_stat_in(16'haaaa/*ca0_stat*/),
	.ca1_stat_in(16'haaaa/*ca1_stat*/),
	.ca2_stat_in(16'haaaa/*ca2_stat*/),
	.ca3_stat_in(16'haaaa/*ca3_stat*/),
	.sensor0_in(32'haaaa_aaaa/*sensor0*/),
	.sensor1_in(32'haaaa_aaaa/*sensor1*/),
	.sensor2_in(32'haaaa_aaaa/*sensor2*/),
	.sensor3_in(32'haaaa_aaaa/*sensor3*/),
	.ai0_in(12'haaa/*ai0*/),
	.ai1_in(12'haaa/*ai1*/),
	.ai2_in(12'haaa/*ai2*/),
	.ai3_in(12'haaa/*ai3*/),
	.ai4_in(12'haaa/*ai4*/)
);

endmodule