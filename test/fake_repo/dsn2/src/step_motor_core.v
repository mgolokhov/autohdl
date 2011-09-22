//************************************:))****************************************************************************************
//�����: ������� �.�.
//		 ������� "������� ����������" �����(��) 2009-2010 �.
//******************************************************************************************************************************* 

module step_motor_core(
    input  rst,             // ����� ������ ���
    input  clk,	            //  Clok
    input  [15:0]phi,       // ���� � ������� ������ �� ���� ���� (� ��� ��������)
    input  [15:0]AmpA,      // ��������� ���� ���� � (���� 17000)
    input  [15:0]AmpB,		// ��������� ���� ���� B (�� ���� ���� �� �������� ���������)
    input  [11:0]adc_a_pos, // ������������� ��������� ���� � (adc_ch_1)
    input  [11:0]adc_a_neg, // ������������� ��������� ���� � (adc_ch_2)
    input  [11:0]adc_b_pos, // ������������� ��������� ���� B (adc_ch_3) 
    input  [11:0]adc_b_neg, // ������������� ��������� ���� � (adc_ch_4) 
    input  adc_rdy,         // Ready �� ADC
    input  start,           // ����� ������� ������� ������ �����. ������ ������� 1/(2^11*2e-8)
    output [15:0]e_a,       // ��������������� ���� A
    output [15:0]e_b,  	   	// ��������������� ���� B
    output [15:0]uq,        // �������� ���������� �� ������� B
    output [15:0]ud,  	   	// �������� ���������� �� ������� A
    output [15:0]ia,        // ��� A
    output [15:0]ib,  	   	// ��� B
    output  [15:0]Va,    // ���������� ������� �� ���� �
    output  [15:0]Vb,  	// ���������� ������� �� ���� B   	
    input  [18:0]Kp,  	   	// ����. ����������������� ����� ���. ���� P8.10 ��� ����� ����� 
    input  [18:0]Ki,  	   	// ����. ������������� ����� ���. ���� P8.10
    input  int_rst,		    // ����� ������������� ����� ���. ����
    input  s_mode,          // 0 - ��������� ����, 1 - uq = AmpB; ud = AmpA
    input  [17:0]ap_dt,     // ����������� ��� ����������� � �������������� ����� 0.17 ����������� ������� �������� 4096
    output h11,              // PWM_B_Hi ???
    output h21,              // PWM_A_Hi ???
    output l11,              // PWM_B_Lo ???
    output l21, 	            // PWM_A_Lo ???
    output h12,              // PWM_B_Hi ???
    output h22,              // PWM_A_Hi ???
    output l12,              // PWM_B_Lo ???
    output l22, 	            // PWM_A_Lo ???
    output [15:0]pa,        // ���� � ��. ��������
    input [15:0] dead_int,
    output p_rdy            // ��� Ready.
    );	  
    

//    wire [11:0]ia_pbias; //���� ������������� ��������� ia
//    wire [11:0]ia_nbias; //���� ������������� ��������� ia             
//    wire [11:0]ib_pbias; //���� ������������� ��������� ib
//    wire [11:0]ib_nbias; //���� ������������� ��������� ib             

    reg init_start;
    
    always @(posedge clk, posedge rst)
        if(rst)
            init_start <= 1;
        else
            if(init_start)
                init_start <= 0;
    
                
/*
    current_bias_init_core ia_init_bias (.rst(rst),
        .clk(clk),
        .start(init_start),
        .ia(adc_a_pos),
        .ib(adc_a_neg),
        .adc_rdy(adc_rdy),
        .ia_bias(ia_pbias),
        .ib_bias(ia_nbias),
        .rdy()
        );
    
    current_bias_init_core ib_init_bias (.rst(rst),
        .clk(clk),
        .start(init_start),
        .ia(adc_b_pos),
        .ib(adc_b_neg),
        .adc_rdy(adc_rdy),
        .ia_bias(ib_pbias),
        .ib_bias(ib_nbias),
        .rdy()
        );
        */
        
        
        
        parameter ia_pbias = 0;
        parameter ia_nbias = 0;
        parameter ib_pbias = 0;
        parameter ib_nbias = 0;
    
    wire [12:0]ia_p;  //������������� ��������� ia
    wire [12:0]ia_n;  //������������� ��������� ia
    wire [12:0]ib_p;  //������������� ��������� ib
    wire [12:0]ib_n;  //������������� ��������� ib
    
    assign ia_p = adc_a_pos - ia_pbias; 
    assign ia_n = adc_a_neg - ia_nbias; 
    assign ib_p = adc_b_pos - ib_pbias; 
    assign ib_n = adc_b_neg - ib_nbias; 
    
    wire [11:0]iam; //12 bit ia
    wire [11:0]ibm; //12 bit ib
/*    
    icore_2ph #(
        .N(12))
        ia_merge (
        .rst(rst),
        .clk(clk),
        .pos_wave(ia_n),
        .neg_wave(ia_p),
        .result(iam)
        );
        
*/        
        
/*    
    icore_2ph #(
        .N(12))
        ib_merge (
        .rst(rst),
        .clk(clk),
        .pos_wave(ib_n),
        .neg_wave(ib_p),
        .result(ibm)
        );
        
*/

assign iam = -ia_p + ia_n;
assign ibm = -ib_p + ib_n;
    
    wire [18:0]xa;
    wire [18:0]ya;
    wire [36:0]ra;
    
    mult19 Va_mult (
    .a(xa),
    .b(ya),
    .c(ra)
    );

wire [18:0]ia18;
    
aperiodic_core 
Filter_va (
    .rst(rst),
    .clk(clk),
    .start(adc_rdy),
    .x({iam,7'b0}),
    .y(ia18),
    .dt_T(ap_dt),
    .mula(xa),
    .mulb(ya),
    .mulc(ra),
    .mul_busy(),
    .rdy()
);
   
    assign ia ={iam,4'b0};

 //assign ia=ia18[18:3];

    wire [18:0]ib18;
    
    wire [18:0]xb;
    wire [18:0]yb;
    wire [36:0] rb;
    
    mult19 Vb_mult (
    .a(xb),
    .b(yb),
    .c(rb)
    );

aperiodic_core 
Filter_vb (
    .rst(rst),
    .clk(clk),
    .start(adc_rdy),
    .x({ibm,7'b0}),
    .y(ib18),
    .dt_T(ap_dt),
    .mula(xb),
    .mulb(yb),
    .mulc(rb),
    .mul_busy(),
    .rdy()
);

 //assign ib=ib18[18:3];
    assign ib ={ibm,4'b0};    

//assign e_a = {iam,4'b0};
//assign e_b = {ibm,4'b0};

    
    wire clk_pwm;
    assign clk_pwm = clk;
  /*  
    DCM vga_dcm (.CLKIN(clk), 
        .RST(1'b0),
        .CLKFX(clk_pwm));
    // synthesis attribute DLL_FREQUENCY_MODE of vga_dcm is "HIGH"
    // synthesis attribute DUTY_CYCLE_CORRECTION of vga_dcm is "TRUE"
    // synthesis attribute STARTUP_WAIT of vga_dcm is "TRUE"
    // synthesis attribute DFS_FREQUENCY_MODE of vga_dcm is "HIGH"
    // synthesis attribute CLKFX_DIVIDE of vga_dcm is 12
    // synthesis attribute CLKFX_MULTIPLY of vga_dcm is 4
    // synthesis attribute CLK_FEEDBACK of vga_dcm  is "NONE"
    // synthesis attribute CLKOUT_PHASE_SHIFT of vga_dcm is "NONE"
    // synthesis attribute PHASE_SHIFT of vga_dcm is 0
    // synthesis attribute clkin_period of vga_dcm is "20.00ns"          
  */  
    parameter reg_k=8;
    
   wire h1_d; 
   wire h2_d; 
    
   dfoc_pwm_core_2ph #(
        .reg_k(8))
        DFOK (
        .rst(rst),
        .clk(clk),
        .clk_pwm(clk_pwm),
        .phi(phi),
        .AmpA(AmpA),
        .AmpB(AmpB),
        .ia(ia),
        .ib(ib),
        .start(start),
        .e_a(e_a),
        .e_b(e_b),
        .uq(uq),
        .ud(ud),
        .Va(Va),
        .Vb(Vb),
        .Kp(Kp),
        .Ki(Ki),
        .int_rst(int_rst),
        .s_mode(s_mode),
        .h11(h11),
        .h21(h21),
        .l11(l11),
        .l21(l21),
        .h12(h12),
        .h22(h22),
        .l12(l12),
        .l22(l22),
        .pa(pa),
        .dead_int(dead_int),
        .p_rdy(p_rdy)
        );    


endmodule	