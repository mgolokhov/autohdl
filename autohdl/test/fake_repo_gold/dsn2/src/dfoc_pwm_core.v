//************************************Модуль расчета FOC c датчикам тока******************************************************
//Модуль расчет напряжений на фазах трехфазного	синхронного двигателя по методу Field Oriented Control (FOC)
//
//
//Входы:
//	rst			- Асинхронный сброс
//	clk	 		- Тактовый генератор
//	clk_pwm		- Тактовый генератор для ШИМ-генератора
//	phi        	- Значение датчика положения (32-бита знаковое)
//  Amp       	- Амплитуда по оси d  в преобразовании Парка (16-бит знаковое)
//  ia          - Ток фазы U
//  ib          - Ток фазы V
//	phase_bias	- Разница между 0 датчика положения и 0 положением ротора в электрических радианах (pi=2^15) (16-бит знаковое)
//	start		- Строб начала расчета		
//  Kp			- Коэффициент пропорционального звена регулятора тока (19-бит, знаковое, reg_k бит целой части)
//  Ki			- Коэффициент интегрального звена регулятора тока (19-бит, знаковое, reg_k бит целой части)
//  int_rst		- Синхронный сброс интегральной составляющей регулятора тока (активный уровень 1)
//  dead_time   - Ассиметрия ШИМ в сторону hi, на каждом цикле ШИМ в тактах clk (11 бит, беззнаковое)	   
//  s_mode		- Отключает контур тока, позволяя перевести двигатель в шаговый режим (0 - с контуром тока, 1 - без контура тока)
//  iq_up		- Высота ступеньки, компенсирующей зону нечувствительности напряжения по оси q (14 бит, беззнаковое)		 
//
//Выходы:					
//  iq			- Ток обмотки q (16-бит знаковое)
//  id			- Ток обмотки d	(16-бит знаковое)			  
//  ud			- Напяржение по оси d 
//  uq			- Напяржение по оси q 
//  i_a			- Координата альфа вектора тока из преобразования Кларка (16-бит знаковое)
//  i_b			- Координата бета вектора тока из преобразования Кларка (16-бит знаковое)					
//  h1-h3		- Верхний транзистор фазы 1-3
//  l1-l3		- Нижний транзистор фазы 1-3	
//  pa			- Угол поворота поля в электрических радианах (16 бит, pi=2^15)
//	rdy			- Флаг окончания вычислений
//
//Параметры:
//	reg_k    	- Количесвто бит целой части в коэффициентах регулятора тока
//	sm_k    	- Коэфициент преобразования положения по датчику в электрические радианы. sm_k=p/N*2^16; (16-бит беззнаковое)
//
//
//Автор: Романов А.М.
//		 Кафедра "Проблем управления" МИРЭА(ТУ) 2009-2010 г.
//******************************************************************************************************************************* 

module dfoc_pwm_core(
	input  rst,
	input  clk,	  
	input  clk_pwm,
	input  [31:0]phi,  
	input  [15:0]Amp,  
	input  [15:0]phase_bias,
	input  [15:0]ia,  
	input  [15:0]ib,  
	input  start,
	output [15:0]iq,  
	output [15:0]id,  	   	
	output [15:0]i_a,  
	output [15:0]i_b,  	   	
	output [15:0]uq,  
	output [15:0]ud,  	   	
	output [15:0]Va,  
	output [15:0]Vb,  	   	
	input  [18:0]Kp,  	   	
	input  [18:0]Ki,  	   	
	input  [10:0]dead_time,		 
//	input  [15:0]iq_up,		 
	input  [15:0]iq_bias,		 
	input  int_rst,		   
	input  s_mode,
	output h1,
	output h2,
	output h3,	  
	output l1,
	output l2,
	output l3,	  	
	output [15:0]pa,
//	output [15:0]iq_corrector,
	output [15:0]iq_sin,
	output rdy,
	output p_rdy
	);	  
	
parameter sm_k=-1;
parameter reg_k=6;//6;   //Кол-во бит целой части коэффициентов регулятора тока

//***********Умножитель*************
//Переключение умножителя между обратным преобразованиями Парка и Кларка	   
wire  [15:0]a;	//16 битный вход умножителя mult16
wire  [15:0]b;	//16 битный вход умножителя mult16
wire  [15:0]c;	//16 битный выход умножителя mult16	 

wire [15:0]p_a;	//16 выход блока обратного преобразования парка к умножителю mult16
wire [15:0]p_b;	//16 выход блока обратного преобразования парка к умножителю mult16  

wire [15:0]cp_a; //16 выход прямого преобразования парка-кларка к умножителю mult16
wire [15:0]cp_b; //16 выход прямого преобразования парка-кларка к умножителю mult16

reg [18:0]a19;	 //19 битный вход умножителя mult19
reg [18:0]b19;	 //19 битный вход умножителя mult19
wire [36:0]c19;  //37 битный выход умножителя mult19
assign c = c19[30:15];

mult19 m19_dfoc (	 //19 битный знаковый умножитель mult19
	.a(a19),
	.b(b19),
	.c(c19)
);

//Переключение умножителя между обратным преобразованиями Парка, преобразованием Кларка и регуляторами
wire [18:0]ad;	 //Выход регулятора	координаты d вектора тока на умножитель mult19
wire [18:0]aq;   //Выход регулятора	координаты q вектора тока на умножитель mult19

wire [18:0]bd;	 //Выход регулятора	координаты d вектора тока на умножитель mult19
wire [18:0]bq;   //Выход регулятора	координаты q вектора тока на умножитель mult19			

reg [1:0]mult_state;  //Регистр состояния умножителя

wire cp_rdy; 			//Флаг окончания прямого преобразования Кларка-Парка
wire pi_d_rdy;			//Флаг окончания рачета регулятора по оси d
wire pi_q_rdy;			//Флаг окончания рачета регулятора по оси q
wire i_park_rdy;   		//Флаг окончания рачета обратного преобразования Парка

always @(posedge rst, posedge clk)		 //Селектор переключающий входы умножителя mult19
	if(rst)
		begin 
			mult_state <= 0;
		end	else
		begin 
			case(mult_state)
				2'b00: 	if(cp_rdy)     mult_state <= mult_state+1;
				2'b01: 	if(pi_d_rdy)   mult_state <= mult_state+1;
				2'b10: 	if(pi_q_rdy)   mult_state <= mult_state+1;
				2'b11: 	if(i_park_rdy) mult_state <= mult_state+1;						   
			endcase	
		end			
		
always @(*)				//Переключение входов умножителя
	case(mult_state)
		2'b00: 	begin 
					a19 <= {cp_a[15],cp_a[15],cp_a[15],cp_a};
					b19 <= {cp_b[15],cp_b[15],cp_b[15],cp_b};
				end	
		2'b01: 	begin 
					a19 <= ad;
					b19 <= bd;
				end
		2'b10: 	begin 
					a19 <= aq;
					b19 <= bq;
				end
		2'b11: 	begin 
					a19 <= {p_a[15],p_a[15],p_a[15],p_a};
					b19 <= {p_b[15],p_b[15],p_b[15],p_b};
				end
	endcase	
	
	
	
//**************Расчет синуса и косинуса угла поворота ротора********************
wire [15:0]sin;
wire [15:0]cos;		

wire sincos_start;
wire sincos_rdy;	   
wire [15:0]z0;		
wire [15:0]c32;
reg [15:0]c32_reg;

//Смещение угла поворота поля по датчику положения на phase_bias
assign z0 = c32_reg + phase_bias;
assign pa=z0;											  

//Перевод датчика положения в электрические радианы ротора
mult_sens_32_v2 mul_sens (
	.a(phi[31:0]),
	.b(sm_k),
	.c(c32)
);	

always @(posedge rst, posedge clk)	//Фиксируем результат умножения, дабы улучшить временные зависимости.
	if(rst)
		c32_reg <= 0;
	else
		c32_reg <= c32;

assign sincos_start =  p_rdy;//start;

//Вычисление sin и cos для прямого и обратного преобразования Парка
cordic_core_v2 sincos_gen (
	.reset(rst),
	.clock(clk),
	.start(sincos_start),
	.z0(z0),
	.finish(sincos_rdy),
	.sin(sin),
	.cos(cos)
);													  

//Компенсатор нелинейного момента

//wire [15:0]z_3o;  //Компенсатор нелинейности момента
//wire [15:0]z_nl;				 
//wire [15:0]sin_iq;
//
//assign z_3o = z0+z0+z0;
//assign z_nl = {z_3o[14:0],1'b0} + iq_bias;	//6*положение ротора+смешение
//
//cordic_core_v2 iq_up_sincos_gen (
//	.reset(rst),
//	.clock(clk),
//	.start(sincos_start),
//	.z0(z_nl),
//	.finish(),
//	.sin(sin_iq),
//	.cos()
//);

//assign iq_sin = sin_iq;

//mult16 SinIQMult (
//	.a(sin_iq),
//	.b({1'b0,iq_up}),
//	.c(iq_corrector)
//);
//

//************Формирования поля*******************
//Прямые преобразования Кларка и Парка 		  
ClarkParkTransform 
clark_park (
	.rst(rst),
	.clk(clk),
	.start(sincos_rdy),
	.ia(ib),
	.ib(ia),
	.sin(sin),
	.cos(cos),
	.mula(cp_a),
	.mulb(cp_b),
	.mulc(c),
	.mul_busy(),
	.id(id),
	.iq(iq),	
	.i_a(i_a),
	.i_b(i_b),
	.rdy(cp_rdy)
);		

//Регуляторы координат q и d
wire [18:0]u_d;	
wire [16:0]e_d;	 	
assign e_d[16:0] = {iq_bias[15],iq_bias}-{id[15],id};

wire [18:0]u_q;	
wire [16:0]e_q;	 	
assign e_q[16:0] = {Amp[15],Amp}-{iq[15],iq};

PI_Regulator #(
	.k(reg_k))
PId (
	.rst(rst),
	.clk(clk),
	.start(cp_rdy),
	.e({e_d,2'd0}),
	.Kp(Kp),
	.Ki(Ki),
	.u(u_d),
	.rdy(pi_d_rdy),
	.int_rst(int_rst),
	.a(ad),
	.b(bd),
	.mul_busy(), 
	.acc_out(),
	.c(c19)
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
	.rdy(pi_q_rdy),
	.int_rst(int_rst),
	.a(aq),
	.b(bq),
	.mul_busy(),
	.acc_out(iq_sin),
	.c(c19)
);		   		 

wire [16:0]u_q_up;		//Разница с учетом переполнения
reg  [15:0]uq_up;		//Ограниченная разница
assign u_q_up = /*{u_q[18]} ? */{u_q[18],u_q[18:3]};// - {iq_bias[15],iq_bias} : {u_q[18],u_q[18:3]} + {iq_bias[15],iq_bias};
//{iq_corrector[15],iq_corrector[15:0]}; //Добавление компенсатора нелинейности по току

always @(*)
	if(u_q_up[16])						  //Ограничение uq
		begin 
			if(u_q_up[15])
				uq_up <= u_q_up[15:0];
			else
				uq_up <=16'h8000;
		end else
		begin 
			if(u_q_up[15])
				uq_up <=16'h7FFF;
			else
				uq_up <= u_q_up[15:0];
		end	

assign ud=(s_mode) ? 0   : u_d[18:3];		//В зависимости от флага перехода в шаговый режим выбирается вход для обратного преобразования Парка
assign uq=(s_mode) ? Amp : uq_up[15:0];		//В зависимости от флага перехода в шаговый режим выбирается вход для обратного преобразования Парка


//Обратное преобразование Парка
InverseParkTransform i_park (
	.rst(rst),
	.clk(clk),
	.start(pi_q_rdy),
	.Vd(ud),
	.Vq(uq),
	.sin(sin),
	.cos(cos),
	.mula(p_a),
	.mulb(p_b),
	.mulc(c),
	.mul_busy(),
	.Va(Va),
	.Vb(Vb),
	.rdy(i_park_rdy)
);				  

assign rdy = i_park_rdy;  


//Генератор пространственно векторной широтно импульсной модуляции
//sv_pwm #(	   
//	.k(12),
//	.sqrt1div3(11'd1182)  /*11'd1182 /*13'd4730*//*15'd18919*//*14'd9459*/
//	)
//SV_PWM(.rst(rst),
//	.clk(clk_pwm),
//	.va(Va[15:4]),
//	.vb(Vb[15:4]), 
//	.dead_time(dead_time),
//	.h1(h1),
//	.l1(l1),
//	.h2(h2),
//	.l2(l2),
//	.h3(h3),
//	.l3(l3),
//	.rdy(p_rdy));		

sin_pwm #(
	.k(12))
SIN_PWM (
	.rst(rst),
	.clk(clk_pwm),
	.va(Va),
	.vb(Vb),
	.dead_time({4'd0,dead_time}),
	.h1(h1),
	.l1(l1),
	.h2(h2),
	.l2(l2),
	.h3(h3),
	.l3(l3),
	.rdy(p_rdy)
);

endmodule	