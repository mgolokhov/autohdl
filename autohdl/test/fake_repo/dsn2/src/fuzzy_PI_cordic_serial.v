//***********************************Нечеткий регулятор**************************************************************
//Романов А.М. Кафедра "Проблемы управления" МИРЭА, 2010 г.
//ВАЖНО: x-b+b1, x-b-b1, x-b - для любого a*x[-1:1] окажутся в дипазоне от [-1:1], перед поступлением на умножители, т.к.
//сигмода всегда лежит [0 1]
//а вот x_arg может и не оказаться. Но для s [0 1] вроде как x_arg лежит [-2 2] (надо б еще потестить)
//*******************************************************************************************************************

module fuzzy_PI_cordic_serial
	#(parameter  N=16, 			//Число бит входа и коэффициентов
      parameter  bN=2,           //Число бит целой части b,b1 и s  
      parameter  aN=4           //Число бит целой части a0,a1 
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
	output reg [N-1:0]out,          //Выход активационной функции
	output reg rdy			    	//Флаг окончания вычислений
	);



reg af_start;
reg [N-1:0]af_x;
reg [N-1:0]af_a0;
reg [N-1:0]af_a1;
reg [N-1:0]af_b;
reg [N-1:0]af_b1;
reg [N-1:0]af_w;
reg [N-1:0]af_s;
reg [1:0]af_ft;

wire af_rdy;            //флаг готовности результата на выходе активационной функции
wire [N-1:0]af_result;


rbf_actfunc_cordic      //Активационная функция по входу x(левая функция принадлежности)
	#(.N(N), 			//Число бит входа и коэффициентов
      .bN(bN),           //Число бит целой части b,b1 и s  
      .aN(aN)
	) af_core
	(
	.rst(rst),			//Асинхронный сброс
	.clk(clk),			//Тактовый генератор
	.start(af_start),		//Строб старта
	.x(af_x),				//Вход [-1 1]
	.a0(af_a0),			//Коэффициент a0=sqrt(w)*sqrt(1-exp(-0.5))/s
	.a1(af_a1),			//Коэффициент a1=sqrt(w)*sqrt((1-exp(-0.5))./s./(b1-s))
    .b(af_b),           //параметр b - середина сигмоиды
    .b1(af_b1),         //параметр b1=s/(1-exp(-0.5))
    .s(af_s),           //параметр s - сигма сигмоиды 
    .w(af_w),           //весовой коэффициент [-1 1]
    .func_type(af_ft),  //типа активационной функции    
	.y(af_result),	 	    //Выход активационной функции в виде потока
	.rdy(af_rdy)	  	//Флаг выхода первого бита результата
	);



reg start_c;   //Строб старта умножителя
reg [N-1:0]mult_a;  //множитель а
reg [N-1:0]mult_b;  //множитель b
wire [N-1:0]mult_c; //результат умножения
wire mult_rdy;       //флаг готовности результата

cordic_mult #(.N(N))                //Умножитель, реализующий правила
        fuzzy_multiplier
    (.clk(clk),
     .rst(rst),
     .a(mult_a),
     .b(mult_b),
     .start(start_c),
     .c(mult_c),
     .rdy(mult_rdy));

reg [N-1:0]y_left;  //результат перемножения левых термов по входу x и y

//typedef enum logic[5:0] {  
parameter
	st_idle			= 6'b000001,
    st_af_xl        = 6'b000010,
    st_af_yl        = 6'b000100,
    st_af_xr        = 6'b001000,
    st_af_yr        = 6'b010000,
	st_mul_right	= 6'b100000
	;//} MultState;
	
	reg [5:0] /*MultState*/ state;
always @(posedge clk, posedge rst)
    if(rst)
        begin
            mult_a <= 0;
            mult_b <= 0;
            start_c <= 0;
            state <=  st_idle;
            out <= 0;
            rdy <= 0;
            y_left <= 0;
            af_start <= 0;
            af_x <= 0;
            af_a0 <= 0;
            af_a1 <= 0;
            af_b <= 0;
            af_b1 <= 0;
            af_w <= 0;
            af_s <= 0;
            af_ft <= 0;
        end else
        case (state)
            st_idle:
                begin
                    if(start)
                        begin
                            af_start <= 1;   //Запускаем вычисление левой активационной функции x
                            af_x <= x;
                            af_a0 <= a0_xl;
                            af_a1 <= a1_xl;
                            af_b <= b_xl;
                            af_b1 <= b1_xl;
                            af_w <= w_xl;
                            af_s <= s_xl;
                            af_ft <= ft_xl;                           
                            state <= st_af_xl;
                        end
                    rdy<=0;
                end
            st_af_xl:
                begin
                    if(af_rdy)
                    begin
                        mult_a <= af_result;  //cохраняем результат в первый вход умножителя
                        af_start <= 1;   //Запускаем вычисление левой активационной функции y
                        af_x <= y;
                        af_a0 <= a0_yl;
                        af_a1 <= a1_yl;
                        af_b <= b_yl;
                        af_b1 <= b1_yl;
                        af_w <= w_yl;
                        af_s <= s_yl;
                        af_ft <= ft_yl;                           
                        state <= st_af_yl;
                    end else
                        af_start <= 0;
                end
            st_af_yl:
                begin
                    if(af_rdy)
                        begin   
                            mult_b <= af_result;  //cохраняем результат во второй вход умножителя
                            af_start <= 1;   //Запускаем вычисление правой активационной функции x
                            af_x <= x;
                            af_a0 <= a0_xr;
                            af_a1 <= a1_xr;
                            af_b <= b_xr;
                            af_b1 <= b1_xr;
                            af_w <= w_xr;
                            af_s <= s_xr;
                            af_ft <= ft_xr;                           
                            start_c <= 1;           //Запускаем умножение результатов левых активационных функций x и y
                            state <= st_af_xr;
                        end else
                            af_start <= 0;  
                end
            st_af_xr:
                begin
                    if(af_rdy)
                    begin
                        mult_a <= af_result;  //cохраняем результат в первый вход умножителя
                        y_left <= mult_c;  //сохраняем результат умножения (которое выполняется быстрее чем расчет активационной функции)
                        af_start <= 1;   //Запускаем вычисление правой активационной функции y
                        af_x <= y;
                        af_a0 <= a0_yr;
                        af_a1 <= a1_yr;
                        af_b <= b_yr;
                        af_b1 <= b1_yr;
                        af_w <= w_yr;
                        af_s <= s_yr;
                        af_ft <= ft_yr;                           
                        state <= st_af_yr;
                    end else
                        begin
                            af_start <= 0;
                            start_c <=0;
                        end
                end
            st_af_yr:
                begin
                    if(af_rdy)
                        begin   
                            mult_b <= af_result;  //cохраняем результат во второй вход умножителя
                            start_c <= 1;        //Запускаем умножение результатов правых активационных функций x и y
                            state <= st_mul_right;
                        end else
                            af_start <= 0; 
                end            
            st_mul_right:
                begin
                    if(mult_rdy)
                        begin
                            out <= mult_c - y_left;   //Выводим в результат разницу между правилами
                            rdy <=1;                  //выставляем флаг готовности
                            state <= st_idle;
                        end else
                            start_c <= 0;
                end            
        endcase


endmodule
