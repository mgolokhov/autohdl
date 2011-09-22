//************************************:))****************************************************************************************
//�����: ������� �.�.
//		 ������� "������� ����������" �����(��) 2009-2010 �.
//******************************************************************************************************************************* 
`default_nettype none
module dfoc_pwm_core_2ph(
    input  rst,
    input  clk,	  
    input  clk_pwm,
    input  [15:0]phi,  
    input  [15:0]AmpA,  
    input  [15:0]AmpB,		 
    input  [15:0]ia,  
    input  [15:0]ib,  
    input  start,
    output [15:0]e_a,  
    output [15:0]e_b,  	   	
    output [15:0]uq,  
    output [15:0]ud,  	   	
    output reg [15:0]Va,  
    output reg [15:0]Vb,  	   	
    input  [18:0]Kp,  	   	
    input  [18:0]Ki,  	   	
    input  int_rst,		   
    input  s_mode,
    output h11,
    output h21,
    output l11,
    output l21, 	
    output h12,
    output h22,
    output l12,
    output l22, 	
    output [15:0]pa,
    input [15:0] dead_int,
    output p_rdy
    );	  
    
    parameter reg_k=6;//6;   //���-�� ��� ����� ����� ������������� ���������� ����
    
    //������������ ���������� ����� �������� ���������������� �����, ��������������� ������ � ������������
    wire [18:0]ad;	 //����� ����������	���������� d ������� ���� �� ���������� mult19
    wire [18:0]aq;   //����� ����������	���������� q ������� ���� �� ���������� mult19
    
    wire [18:0]bd;	 //����� ����������	���������� d ������� ���� �� ���������� mult19
    wire [18:0]bq;   //����� ����������	���������� q ������� ���� �� ���������� mult19		        
         
    
    //**************������ ������ � �������� ���� �������� ������********************
    
    wire sincos_start;
    wire sincos_rdy;	   
    wire [15:0]z0;		
    reg [15:0]z_reg;
    
    //�������� ���� �������� ���� �� ������� ��������� �� phase_bias
    assign z0 = z_reg;
    assign pa=z0;											  
    
    //������� ������� ��������� � ������������� ������� ������
    
    always @(posedge rst, posedge clk)	//��������� ��������� ���������, ���� �������� ��������� �����������.
        if(rst)
            z_reg <= 0;
        else
            z_reg <= /*50**/phi;
    
    assign sincos_start = start;
    
    //���������� sin � cos ��� ������� � ��������� �������������� �����
    
    wire [15:0]sin;  
    wire [15:0]cos;
    
    cordic_core_v3 #(
        .N(16))
    cordic_core (.rst(rst),
        .clk(clk),
        .start(sincos_start),
        .value(z0),
        .sin(sin),
        .cos(cos),
        .rdy(sincos_rdy)
    );
    
    
    wire [15:0]w_Va;
    wire [15:0]w_Vb;
    
    mult16 Va_mult (
    .a(sin),
    .b(AmpA),
    .c(w_Va)
    );

    mult16 Vb_mult (
    .a(cos),
    .b(AmpB),
    .c(w_Vb)
    );
    
    
   
    always @(posedge clk, posedge rst)
        if(rst)
            begin 
                Va <=0;
                Vb <=0;
            end else
            begin 
                Va <= w_Va;
                Vb <= w_Vb;
            end    

    reg start_reg;
    
    always @(posedge clk, posedge rst)
        if(rst)
            start_reg <= 0;
        else 
            start_reg <= sincos_rdy;
            
    //���������� ��������� a=d � b=q
    wire [18:0]u_d;	
    wire [16:0]e_d;	 	
    assign e_d[16:0] = {Va[15],Va}-{ia[15],ia};
    
    wire [18:0]u_q;	
    wire [16:0]e_q;	 	
    assign e_q[16:0] = {Vb[15],Vb}-{ib[15],ib};

    assign e_a = e_d[16:0];
    assign e_b = e_q[16:0];
 
    
    wire [36:0]c19_rd;  //37 ������ ����� ���������� mult19

    mult19 m19_dfoc_rd (	 //19 ������ �������� ���������� mult19
        .a(ad),
        .b(bd),
        .c(c19_rd)
        );	
    
    wire pi_d_rdy;        
    
    PI_Regulator #(
        .k(reg_k))
        PId (
        .rst(rst),
        .clk(clk),
        .start(start_reg),
        .e({e_d,2'd0}),
        .Kp(Kp),
        .Ki(Ki),
        .u(u_d),
        .rdy(pi_d_rdy),
        .int_rst(int_rst),
        .a(ad),
        .b(bd),
        .mul_busy(), 
        .mul_rdy(1),
        .mul_start(),
        .acc_out(),
        .c(c19_rd)
        );	

    wire [36:0]c19_rq;  //37 ������ ����� ���������� mult19

    mult19 m19_dfoc_rq (	 //19 ������ �������� ���������� mult19
        .a(aq),
        .b(bq),
        .c(c19_rq)
        );	
        
        
    PI_Regulator #(
        .k(reg_k))
        PIq (
        .rst(rst),
        .clk(clk),
        .start(pi_d_rdy),
        .e({e_q,2'd0}),
        .Kp(Kp),
        .Ki(Ki),
        .u(u_q),
        .rdy(),
        .int_rst(int_rst),
        .a(aq),
        .b(bq),
        .mul_busy(),
        .mul_rdy(1), 
        .mul_start(),
        .acc_out(),
        .c(c19_rq)
        );		   		 
    
        
    assign ud=(s_mode) ? AmpA : (int_rst ? 0 :u_d[18:3]);		//� ����������� �� ����� �������� � ������� ����� ���������� ���� ��� ��������� �������������� �����
    assign uq=(s_mode) ? AmpB : (int_rst ? 0 :u_q[18:3]);		//� ����������� �� ����� �������� � ������� ����� ���������� ���� ��� ��������� �������������� �����
    
       
    reg pp;
    wire prdy;
    
    assign p_rdy = pp;
    
    always @(posedge clk, posedge rst)
        if(rst)
            pp <= 0;
        else
            pp <= prdy;
            
 wire [15:0] uq_di;
 
 dead_interval_core dic1(
    .clk(clk),
    .rst(rst),
    .val_in(uq),
    .pos_int(24),
    .neg_int(36),
    .val_out(uq_di)
);
    
    pwm_core_hl #(
        .k(12),
        .znak(1'b0))
        Va_pwm_core (
        .rst(rst),
        .clk(clk_pwm),
        .dead_int(dead_int),
        .val_in(uq_di),
        .h_out(h11),
        .l_out(l11),
        .pwm_ready(prdy)
        );
        
    pwm_core_hl #(
        .k(12),
        .znak(1'b1))
        Va_pwm_core2 (
        .rst(rst),
        .clk(clk_pwm),
        .dead_int(dead_int),
        .val_in(uq_di),
        .h_out(h12),
        .l_out(l12),
        .pwm_ready()
        );
        
 wire [15:0] ud_di;
 dead_interval_core dic2(
    .clk(clk),
    .rst(rst),
    .val_in(ud),
    .pos_int(24),
    .neg_int(36),
    .val_out(ud_di)
);        
    
    pwm_core_hl #(
        .k(12),
        .znak(1'b0))
        Vb_pwm_core (
        .rst(rst),
        .clk(clk_pwm),
        .dead_int(dead_int),
        .val_in(ud_di),
        .h_out(h21),
        .l_out(l21),
        .pwm_ready()
        );

        pwm_core_hl #(
        .k(12),
        .znak(1'b1))
        Vb_pwm_core2 (
        .rst(rst),
        .clk(clk_pwm),
        .dead_int(dead_int),
        .val_in(ud_di),
        .h_out(h22),
        .l_out(l22),
        .pwm_ready()
        );
    
endmodule	