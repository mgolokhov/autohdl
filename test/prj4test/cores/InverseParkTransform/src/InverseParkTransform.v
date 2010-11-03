//************************************Модуль расчета обратного преобразованя Парка**********************************
//Модуль выполняет обратное преобразования Парка
//Для работы модуля требуется умножитель mult16 или аналогичный аппаратный умножитель двух чисел (16-бит, знаковое 
//с фиксированной точкой, 0-бит целой части, 15 бит дробной части)
//
//Входы:
//	rst		- Асинхронный сброс
//	clk		- Тактовый генератор
//	start	- Строб начала расчета
//	Vd		- Координата d вектора напряжения в преобразовании Парка (16-бит знаковое)
//	Vq		- Координата q вектора напряжения в преобразовании Парка (16-бит знаковое)
//	sin		- Синус угла вектора магнитной индукции поля ротора, относительно поля статора 
//			  (16-бит знаковое, с фикс. точкой 0-бит целой части, 15 бит дробной части)
//	cos		- Косинус угла вектора магнитной индукции поля ротора, относительно поля статора 
//			  (16-бит знаковое, с фикс. точкой 0-бит целой части, 15 бит дробной части)
//	mulc	- Вход с внешнего умножителя mult16 
//
//Выходы:
//	mula	- Выход на внешний умножитель mult16
//	mulb	- Выход на внешний умножитель mult16				  
//  mul_busy- Флаг того, что умножитель занят
//	Va		- Координата альфа вектора напряжения в преобразовании Кларка (16-бит знаковое)
//	Vb		- Координата бета вектора напряжения в преобразовании Кларка (16-бит знаковое)
//	rdy		- Флаг окончания вычислений
//
//Автор: Романов А.М.
//		 Кафедра "Проблем управления" МИРЭА(ТУ) 2009 г.
//***********************************************************************************************************************

module InverseParkTransform(
	input  rst,                  //Асинхронный сброс
	input  clk,					 //Тактовый генератор
	input  start,				 //Строб начала расчета
	input  [15:0]Vd,			 //Координата d вектора тока в преобразовании Парка (16-бит знаковое)
	input  [15:0]Vq,			 //Координата q вектора тока в преобразовании Парка (16-бит знаковое)
	input  [15:0]sin,			 //Синус угла вектора магнитной индукции поля ротора, относительно поля статора
	input  [15:0]cos,			 //Косинус угла вектора магнитной индукции поля ротора, относительно поля статора
	output reg [15:0]mula,		 //Выход на внешний умножитель mult16
	output reg [15:0]mulb,		 //Выход на внешний умножитель mult16
	input  [15:0]mulc,			 //Вход с внешнего умножителя mult16
	output mul_busy,			 //Флаг того, что умножитель занят
	output reg [15:0]Va,		 //Координата альфа вектора тока в преобразовании Кларка
	output reg [15:0]Vb,         //Координата бета вектора тока в преобразовании Кларка	
	output reg rdy);             //Флаг окончания вычислений

//typedef enum logic[4:0] {
parameter
	st_idle			= 5'b00001,
	st_muldcs		= 5'b00010,
	st_muldsn		= 5'b00100,
	st_mulqsn		= 5'b01000,
	st_mulqcs		= 5'b10000
	;//} IPState;					 
	
	reg [4:0] /*IPState*/ state;		
	
reg [15:0]s_Vq;
reg [16:0]t_Va;	
reg [15:0]t_Vb;	  
wire [16:0]t_Vb_sum;

assign t_Vb_sum = {t_Vb[15],t_Vb}+{mulc[15],mulc}; 

wire [18:0]Va_mul_3;
wire [18:0]Vb_mul_3;

assign Va_mul_3 = {t_Va[16],t_Va,1'b0}+{t_Va[16],t_Va[16],t_Va};                        //Значение Va * 3;
assign Vb_mul_3 = {t_Vb_sum[16],t_Vb_sum,1'b0}+{t_Vb_sum[16],t_Vb_sum[16],t_Vb_sum};	//Значение Vb * 3; 

reg [15:0]Va_sat;   //Ограниченное значения Va*3/4	   
reg [15:0]Vb_sat;	//Ограниченное значения Va*3/4	   

always @(*)
	begin 
		if(t_Va[16])
			begin 
				if(t_Va[15])
					Va_sat <= t_Va[15:0];
				else 
					Va_sat <= 16'h8000;
			end	else	
			begin 
				if(t_Va[15])
					Va_sat <= 16'h7FFF;
				else
					Va_sat <= t_Va[15:0];					
			end				
	end	

always @(*)
	begin 
		if(t_Vb_sum[16])
			begin 
				if(t_Vb_sum[15])
					Vb_sat <= t_Vb_sum[15:0];
				else 
					Vb_sat <= 16'h8000;
			end	else	
			begin 
				if(t_Vb_sum[15])
					Vb_sat <= 16'h7FFF;
				else
					Vb_sat <= t_Vb_sum[15:0];					
			end				
	end	
	
//always @(*)			//Ограничение Va и деление на 4
//	begin 
//		if(Va_mul_3[18])
//			begin 
//				if(Va_mul_3[17])
//					Va_sat <= Va_mul_3[17:2];
//				else
//					Va_sat <= 16'h8001;
//			end else
//			begin  
//				if(Va_mul_3[17])
//					Va_sat <= 16'h7FFF;		
//				else
//					Va_sat <= Va_mul_3[17:2];  					
//			end	
//	end				 
//	
//always @(*)			//Ограничение Vb и деление на 4
//	begin 
//		if(Vb_mul_3[18])
//			begin 
//				if(Vb_mul_3[17])
//					Vb_sat <= Vb_mul_3[17:2];
//				else
//					Vb_sat <= 16'h8001;
//			end else
//			begin  
//				if(Vb_mul_3[17])
//					Vb_sat <= 16'h7FFF;		
//				else
//					Vb_sat <= Vb_mul_3[17:2];  					
//			end	
//	end			



always @(posedge rst, posedge clk)
	if(rst)
		begin
			Va<=16'd0;
			Vb<=16'd0;
			rdy<=1'b0;	   
			mula<=16'd0;
			mulb<=16'd0;
			s_Vq<=16'd0;
			t_Va<=16'd0;
			t_Vb<=16'd0;	
			state<=st_idle;
		end else
		case (state)
		st_idle:
			begin
				if(start)
					begin
						s_Vq<=Vq;		   //Сохраняем значения Vq на время вычислений
						mula<=Vd;
						mulb<=cos;
						state<=st_muldcs;
					end
				if(rdy) rdy<=~rdy;		   //Снимаем флаг rdy, если он стоял
			end 
		st_muldcs:
			begin		   
				t_Va<={mulc[15],mulc};				   //Сохраняем Vd*cos, как часть Va
				mulb<=sin;				   //Умножаем Vd*sin
				state<=st_muldsn;
			end
		st_muldsn:
			begin		   
				t_Vb<=mulc;				  //Сохраняем Vd*sin, как часть Vb
				mula<=s_Vq;		 		  //Умножаем Vq*sin
				state<=st_mulqsn;
			end		   
		st_mulqsn:
			begin
				t_Va<=t_Va-{mulc[15],mulc};		  //Вычисляем Va=Vd*cos-Vq*sin
				mulb<=cos;				  //Умножаем Vq*cos
				state<=st_mulqcs;
			end		   
		st_mulqcs:
			begin	  
				Va<=Va_sat;				  //Выводим Va на выход
				Vb<=Vb_sat;			      //Вычисляем Vb=Vd*sin+Vq*cos
				rdy<=1'b1;
				state<=st_idle;
			end
		endcase	
		
assign mul_busy=(state!=st_idle);
		
endmodule	
