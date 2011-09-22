//***********************************Нечеткий регулятор**************************************************************
//Романов А.М. Кафедра "Проблемы управления" МИРЭА, 2010 г.
//ВАЖНО: x-b+b1, x-b-b1, x-b - для любого a*x[-1:1] окажутся в дипазоне от [-1:1], перед поступлением на умножители, т.к.
//сигмода всегда лежит [0 1]
//а вот x_arg может и не оказаться. Но для s [0 1] вроде как x_arg лежит [-2 2] (надо б еще потестить)
//*******************************************************************************************************************

module fuzzy_PI
	#(parameter  N=16, 			//Число бит входа и коэффициентов
      parameter  bN=2           //Число бит целой части b,b1 и s  
	)	
	(
	input rst,					//Асинхронный сброс
	input clk,					//Тактовый генератор
	input start,				//Строб старта
	input [N-1:0]x,				//Вход x [-1 1]
	input [N-1:0]y,				//Вход y [-1 1]
//(левая функция принадлежноси) 
	input [N-1:0]a0_xl,			//Коэффициент по входу x a0=sqrt(w_x)*sqrt(1-exp(-0.5))/s
	input [N-1:0]a1_xl,			//Коэффициент по входу x a1=sqrt(w_x)*sqrt((1-exp(-0.5))./s./(b1-s))
    input [N-1:0]b_xl ,          //параметр по входу x b - cередина сигмоиды
    input [N-1:0]b1_xl,          //параметр по входу x b1=s/(1-exp(-0.5))
    input [N-1:0]s_xl,            //параметр по входу x s - сигма сигмоиды 
    input [1:0]  ft_xl,          //тип активационной функции
	input [N-1:0]a0_yl,			//Коэффициент по входу y a0=sqrt(w_y)*sqrt(1-exp(-0.5))/s
	input [N-1:0]a1_yl,			//Коэффициент по входу y a1=sqrt(w_y)*sqrt((1-exp(-0.5))./s./(b1-s))
    input [N-1:0]b_yl ,          //параметр по входу y b - cередина сигмоиды
    input [N-1:0]b1_yl,          //параметр по входу y b1=s/(1-exp(-0.5))
    input [N-1:0]s_yl,            //параметр по входу x s - сигма сигмоиды 
    input [1:0]  ft_yl,          //тип активационной функции
    input [N-1:0]w_xl,           //весовой коэффициент по входу x [-1 1]
    input [N-1:0]w_yl,           //весовой коэффициент по входу y [-1 1]
//(правая функция принадлежноси) 
	input [N-1:0]a0_xr,			//Коэффициент по входу x a0=sqrt(w_x)*sqrt(1-exp(-0.5))/s
	input [N-1:0]a1_xr,			//Коэффициент по входу x a1=sqrt(w_x)*sqrt((1-exp(-0.5))./s./(b1-s))
    input [N-1:0]b_xr ,          //параметр по входу x b - cередина сигмоиды
    input [N-1:0]b1_xr,          //параметр по входу x b1=s/(1-exp(-0.5))
    input [N-1:0]s_xr,            //параметр по входу x s - сигма сигмоиды 
    input [1:0]  ft_xr,          //тип активационной функции
	input [N-1:0]a0_yr,			//Коэффициент по входу y a0=sqrt(w_y)*sqrt(1-exp(-0.5))/s
	input [N-1:0]a1_yr,			//Коэффициент по входу y a1=sqrt(w_y)*sqrt((1-exp(-0.5))./s./(b1-s))
    input [N-1:0]b_yr ,          //параметр по входу y b - cередина сигмоиды
    input [N-1:0]b1_yr,          //параметр по входу y b1=s/(1-exp(-0.5))
    input [N-1:0]s_yr,            //параметр по входу x s - сигма сигмоиды 
    input [1:0]  ft_yr,          //тип активационной функции
    input [N-1:0]w_xr,           //весовой коэффициент по входу x [-1 1]
    input [N-1:0]w_yr,           //весовой коэффициент по входу y [-1 1]
	input [Skip_N-1:0]afrac,	//Кол-во бит дробной части коэффициентов a    
	output [N-1:0]out,          //Выход активационной функции
	output rdy			    	//Флаг окончания вычислений
	);


function integer log2;			//Функция выисления логорифма по основанию 2
  input integer value;
  begin
    for (log2=0; value>0; log2=log2+1)
      value = value>>1;
  end
endfunction	

parameter Skip_N=log2(2*(N+1)); //Число бит при хранении пропуска в умножителе (вычисляется по формуле ceil(log2(2*(N+1)), т.к один из умножитель на a N+1 битный 

wire axs_l;       //поток выхода активационной функции входа x(левая функция принадлежности)
wire ays_l;       //поток выхода активационной функции входа y(левая функция принадлежности)
wire axs_r;       //поток выхода активационной функции входа x(правая функция принадлежности)
wire ays_r;       //поток выхода активационной функции входа y(правая функция принадлежности)
wire x_fbit;      //флаг выхода первого бита активационной функции входа x


rbf_actfunc_serial      //Активационная функция по входу x(левая функция принадлежности)
	#(.N(N), 			//Число бит входа и коэффициентов
      .bN(bN)           //Число бит целой части b,b1 и s  
	) af_core_x_left
	(
	.rst(rst),			//Асинхронный сброс
	.clk(clk),			//Тактовый генератор
	.start(start),		//Строб старта
	.x(x),				//Вход [-1 1]
	.a0(a0_xl),			//Коэффициент a0=sqrt(w)*sqrt(1-exp(-0.5))/s
	.a1(a1_xl),			//Коэффициент a1=sqrt(w)*sqrt((1-exp(-0.5))./s./(b1-s))
	.afrac(afrac),	    //Кол-во бит дробной части
    .b(b_xl),           //параметр b - середина сигмоиды
    .b1(b1_xl),         //параметр b1=s/(1-exp(-0.5))
    .s(s_xl),           //параметр s - сигма сигмоиды 
    .w(w_xl),           //весовой коэффициент [-1 1]
    .func_type(ft_xl),  //типа активационной функции    
	.y(axs_l),	 	    //Выход активационной функции в виде потока
	.fbit(x_fbit)	  	//Флаг выхода первого бита результата
	);

rbf_actfunc_serial      //Активационная функция по входу x(правая функция принадлежности)
	#(.N(N), 			//Число бит входа и коэффициентов
      .bN(bN)           //Число бит целой части b,b1 и s  
	) af_core_x_right
	(
	.rst(rst),			//Асинхронный сброс
	.clk(clk),			//Тактовый генератор
	.start(start),		//Строб старта
	.x(x),				//Вход [-1 1]
	.a0(a0_xr),			//Коэффициент a0=sqrt(w)*sqrt(1-exp(-0.5))/s
	.a1(a1_xr),			//Коэффициент a1=sqrt(w)*sqrt((1-exp(-0.5))./s./(b1-s))
	.afrac(afrac),	    //Кол-во бит дробной части
    .b(b_xr),           //параметр b - середина сигмоиды
    .b1(b1_xr),         //параметр b1=s/(1-exp(-0.5))
    .s(s_xr),           //параметр s - сигма сигмоиды 
    .w(w_xr),           //весовой коэффициент [-1 1]
    .func_type(ft_xr),  //типа активационной функции    
  	.y(axs_r),	 	    //Выход активационной функции в виде потока
	.fbit()	  	//Флаг выхода первого бита результата
	);

rbf_actfunc_serial      //Активационная функция по входу y(левая функция принадлежности)
	#(.N(N), 			//Число бит входа и коэффициентов
      .bN(bN)           //Число бит целой части b,b1 и s  
	) af_core_y_left
	(
	.rst(rst),			//Асинхронный сброс
	.clk(clk),			//Тактовый генератор
	.start(start),		//Строб старта
	.x(y),				//Вход [-1 1]
	.a0(a0_yl),			//Коэффициент a0=sqrt(w)*sqrt(1-exp(-0.5))/s
	.a1(a1_yl),			//Коэффициент a1=sqrt(w)*sqrt((1-exp(-0.5))./s./(b1-s))
	.afrac(afrac),	    //Кол-во бит дробной части
    .b(b_yl),           //параметр b - середина сигмоиды
    .b1(b1_yl),         //параметр b1=s/(1-exp(-0.5))
    .s(s_yl),           //параметр s - сигма сигмоиды 
    .w(w_yl),           //весовой коэффициент [-1 1]
    .func_type(ft_yl),  //типа активационной функции    
    
	.y(ays_l),	 	    //Выход активационной функции в виде потока
	.fbit()	  	//Флаг выхода первого бита результата
	);

rbf_actfunc_serial      //Активационная функция по входу x(правая функция принадлежности)
	#(.N(N), 			//Число бит входа и коэффициентов
      .bN(bN)           //Число бит целой части b,b1 и s  
	) af_core_y_right
	(
	.rst(rst),			//Асинхронный сброс
	.clk(clk),			//Тактовый генератор
	.start(start),		//Строб старта
	.x(y),				//Вход [-1 1]
	.a0(a0_yr),			//Коэффициент a0=sqrt(w)*sqrt(1-exp(-0.5))/s
	.a1(a1_yr),			//Коэффициент a1=sqrt(w)*sqrt((1-exp(-0.5))./s./(b1-s))
	.afrac(afrac),	    //Кол-во бит дробной части
    .b(b_yr),           //параметр b - середина сигмоиды
    .b1(b1_yr),         //параметр b1=s/(1-exp(-0.5))
    .s(s_yr),           //параметр s - сигма сигмоиды 
    .w(w_yr),           //весовой коэффициент [-1 1]
    .func_type(ft_yr),  //типа активационной функции    
    
	.y(ays_r),	 	    //Выход активационной функции в виде потока
	.fbit()	  	//Флаг выхода первого бита результата
	);

wire left_s;     //Поток на выходе умножителя левых  ф-ий принадлежности
wire right_s;    //Поток на выходе умножителя правых ф-ий принадлежности
wire mfbit;      //флаг выхода первого бита из умножителя

serial_mult #(				//Последовательный умножитель на лев*лев
	.N(N)
    )
mult_left (
	.rst(rst),              
	.clk(clk),
	.start(x_fbit),
	.a(axs_l),
	.b(ays_l),
	.c(left_s),
	.process(),
    .fbit(mfbit),
    .skip(N-1),
	.rdy()
);	

serial_mult #(				//Последовательный умножитель на прав*прав
	.N(N)
    )
mult_right (
	.rst(rst),              
	.clk(clk),
	.start(x_fbit),
	.a(axs_r),
	.b(ays_r),
	.c(right_s),
	.process(),
    .fbit(),
    .skip(N-1),
	.rdy()
);	

wire out_s;  //поток выходного сумматора

serial_subs sum_out(	//Выходной сумматор
	.rst(rst), 		    //Асинхронный сброс
	.clk(clk), 		    //Тактовый генератор
	.a(right_s),	    //Слогаемое a
	.b(left_s),		    //Слогаемое b		
	.start(mfbit),	    //Синхронный сброс
	.c(out_s),          //Результат сложения
	.ovf()              //Флаг переноса
	);	

reg out_fbit;

always @(posedge clk, posedge rst)
    if(rst)
        out_fbit <= 0;
    else
        out_fbit <= mfbit;

serial_pool 
   #(.N(N)	//На выходе умножителя нас интересует первые N-бит, т.к.
    ) sp (
    .rst(rst),          //Асинхронный сброс
    .clk(clk),          //Тактовый генератор
    .fbit(out_fbit),       //Флаг того, что пришел первый бит
    .x(out_s),          //Вход, последовательное число
    .y(out),            //Выход обычное число N-бит
    .rdy(rdy)           //Флаг того, что вышло новое число
    );


endmodule
