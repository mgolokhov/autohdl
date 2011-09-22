//***********************************Активационная функция RBF - нейрона*********************************************
//Романов А.М. Кафедра "Проблемы управления" МИРЭА, 2010 г.
//ВАЖНО: x-b+b1, x-b-b1, x-b - для любого a*x[-1:1] окажутся в дипазоне от [-1:1], перед поступлением на умножители, т.к.
//сигмода всегда лежит [0 1]
//а вот x_arg может и не оказаться. Но для s [0 1] вроде как x_arg лежит [-2^bN 2^bN] (надо б еще потестить)
//*******************************************************************************************************************

module rbf_actfunc_serial
	#(parameter  N=16, 			//Число бит входа и коэффициентов
      parameter  bN=2           //Число бит целой части b,b1 и s  
	)	
	(
	input rst,					//Асинхронный сброс
	input clk,					//Тактовый генератор
	input start,				//Строб старта
	input [N-1:0]x,				//Вход [-1 1]
	input [N-1:0]a0,			//Коэффициент a0=sqrt(w)*sqrt(1-exp(-0.5))/s
	input [N-1:0]a1,			//Коэффициент a1=sqrt(w)*sqrt((1-exp(-0.5))./s./(b1-s))
	input [Skip_N-1:0]afrac,	//Кол-во бит дробной части
    input [N-1:0]b,             //параметр b - середина сигмоиды
    input [N-1:0]b1,            //параметр b1=s/(1-exp(-0.5))
    input [N-1:0]s,             //параметр s - сигма сигмоиды 
    input [N-1:0]w,             //весовой коэффициент [-1 1]
    input [1:0]func_type,       //Тип активационной функции 0 или 1 - обычная, 2 - левее купола высокий уровент, 3-правее купола высокий уровень
    
	output y,	   	            //Выход активационной функции в виде потока
	output fbit			    	//Флаг выхода первого бита результата
	);


function integer log2;			//Функция выисления логорифма по основанию 2
  input integer value;
  begin
    for (log2=0; value>0; log2=log2+1)
      value = value>>1;
  end
endfunction	

parameter Skip_N=log2(2*(N+1)); //Число бит при хранении пропуска в умножителе (вычисляется по формуле ceil(log2(2*(N+1)), т.к один из умножитель на a N+1 битный 

reg [N+bN:0]dxb;        //x-b
reg [N+bN+1:0]dxb_s/*verilator public*/;    //|x-b|-s или x-b+b1, или x-b-b1

wire [bN-1:0]blow; //младшие знаки b
wire [bN-1:0]b1low; //младшие знаки b1
wire [bN:0]xhi;  //старшие биты x
wire [bN-1:0]slow; //младшие знаки s

assign blow  = (b[N-1])  ? -1 : 0;
assign b1low = (b1[N-1]) ? -1 : 0;
assign slow =  (s[N-1])  ? -1 : 0;
assign xhi   = (x[N-1])  ? -1 : 0;

//typedef enum logic[4:0] {  
parameter
	st_idle			= 5'b00001,
	st_st1   		= 5'b00010,
	st_st2   		= 5'b00100,
	st_st3   		= 5'b01000,
	st_st4   		= 5'b10000
	;//} SelState;
	
	reg [4:0] /*SelState*/ state;						  

reg [1:0]x_pos;  //Положение x
//2'b00 - левее левой параболы или правее правой (т.е. в итоге результат будет равен 0)
//2'b01 - левая или правая парабола парабола y=(a1*(x-b+b1))^2;
//2'b10 - центральная парабола y=w-(a0*(x-b))^2
//2'b11 - левая часть у левой акт-функции и правая часть у правой (высокий уровень)
reg start_c_sel;  //Запуск селектора коэффициентов

always @(posedge clk,posedge rst)
    if(rst)
    begin
        dxb <= 0;
        dxb_s <= 0;
        x_pos <= 2'b00;
        state <= st_idle;
        start_c_sel <= 0;
    end
    else
        case (state)
            st_idle:
                begin
                    if(start)
                        begin
                            dxb <= {xhi,x} - {b[N-1],b,blow};  //Вычисляем x-b
                            state <= st_st1;
                        end
                    start_c_sel <= 0;
                end
            st_st1:
                begin
                    if(dxb[N+bN])                //Вычисляем |x-b|-s
                        dxb_s <= -{dxb[N+bN],dxb}-{s[N-1],s[N-1],s,slow}; 
                    else
                        dxb_s <= {dxb[N+bN],dxb}-{s[N-1],s[N-1],s,slow};
                    x_pos <= 2'b00;
                    start_c_sel <= 0;
                    state <= st_st2;    
                end
            st_st2:
                begin
                    if(func_type[1]&(func_type[0]!=dxb[N+bN]))  //Т.е если активационная функция левая или правая
                    begin
                            x_pos <= 2'b11;  //Если x-b<0 для левой функции или x-b>0 для правой функции, то x - лежит в области постоянного высокого уровня
                    end else
                    if(dxb_s[N+bN+1])  //x находится за диапазоном [-s s]
                        begin
                            dxb_s <= {dxb[N+bN],dxb};
                            x_pos <= 2'b10; //x - в центральной параболе
                        end else
                        begin
                            dxb_s <= {dxb[N+bN],dxb}-{b1[N-1],b1[N-1],b1,b1low};    //x-b-b1
                            x_pos <= 2'b00;
                        end    
                    start_c_sel <= 0;
                    state <= st_st3;    
                end
            st_st3:
                begin
                    if(x_pos==2'b00)
                    begin
                        if(dxb_s[N+bN+1]&(dxb[N+bN]==0))  //x-b-b1<0 и |x-b|>0 и x-b>0
                            begin
                                x_pos <= 2'b01; //x - в правой параболе
                            end else
                            begin
                                dxb_s <= {dxb[N+bN],dxb}+{b1[N-1],b1[N-1],b1,b1low};  //x-b+b1  
                            end    
                    end
                    start_c_sel <= 0;
                    state <= st_st4;    
                end
            st_st4:
                begin
                    if(x_pos==2'b00)
                    begin
                        if((dxb_s[N+bN+1]==0)&dxb[N+bN])  //x-b+b1>0 и |x-b|>0 и x-b<0
                            begin
                                x_pos <= 2'b01; //x - в левой параболе
                            end 
                    end
                    state <= st_idle;    
                    start_c_sel <= 1;  //Запускаем селектор коэффициентов
                end
        endcase


reg [N+bN-1:0]x_arg;  //Значение x с учетом смещения на b, b1 или -b1
reg [N-1:0]a;    //Значение коэффициента a
reg wm;          //Флаг включающий или отключающий смещение на 1   (включено только у центральной параболы)

always @(posedge clk,posedge rst)
    if(rst)
        begin
            x_arg <=0;
        end
    else
        if(start_c_sel)
            begin
                case (x_pos)
                    2'b00: 
                        begin
                            x_arg <= 0;
                            a <= 0;
                            wm <= 0;
                        end
                    2'b01: 
                        begin
                            x_arg <= dxb_s[N+bN-1:0];
                            a <= a1;
                            wm <= 0;
                        end
                    2'b10: 
                        begin
                            x_arg <= dxb_s[N+bN-1:0];
                            a <= a0;
                            wm <= 1;
                        end
                    2'b11: 
                        begin
                            x_arg <= 0;
                            a <= 0;
                            wm <= 1;
                        end
                    default : 
                        begin
                            x_arg <= 0;
                            a <= 0;
                            wm <= 0;
                        end
                endcase
            end

reg start_stream; //Флаг запуска перевода в поток

always @(posedge clk,posedge rst)
    if(rst)
        start_stream <=0;
    else
        start_stream <= start_c_sel;

wire as;  //Поток множителя a
wire xs;  //Поток множителя x_arg
wire start_mult;  //Флаг запуска умножителя

serial_streamer  #(
    .N(N)	    //Число бит входа
    ) ss_a (
    .rst(rst),          //Асинхронный сброс
    .clk(clk),          //Тактовый генератор
    .x(a),              //Вход
    .start(start_stream),      //Строб, по которому 1 раз на выход отдается последовательный поток(а после на выходе поддерживается последний бит этого потока(знак)
    .y(as),           //Очередной бит потока
    .fbit(start_mult)         //Флаг того, что в y выходит первый бит нового числа
    );

serial_streamer  #(
    .N(N+bN)	    //Число бит входа
    ) ss_x (
    .rst(rst),          //Асинхронный сброс
    .clk(clk),          //Тактовый генератор
    .x(x_arg),              //Вход
    .start(start_stream),      //Строб, по которому 1 раз на выход отдается последовательный поток(а после на выходе поддерживается последний бит этого потока(знак)
    .y(xs),           //Очередной бит потока
    .fbit()         //Флаг того, что в y выходит первый бит нового числа
    );

wire axs;   //Поток результата умножения a*x_arg
wire ax_fb; //Флаг выхода первого бита из умножителя a*x_arg;

serial_mult #(				//Последовательный умножитель на a
	.N(N+bN)
    )
mult_a (
	.rst(rst),              
	.clk(clk),
	.start(start_mult),
	.a(as),
	.b(xs),
	.c(axs),
	.process(),
    .fbit(ax_fb),
    .skip(afrac),
	.rdy()
);	

wire sqr_s;                 //Поток (a_x_arg)^2
wire sqr_fb;                //Флаг выхода первого бита потока возведения в квадрат

serial_mult #(				//Последовательный умножитель для возведения в квадрат
	.N(N)
    )
mult_sqr (
	.rst(rst),              
	.clk(clk),
	.start(ax_fb),
	.a(axs),
	.b(axs),
	.c(sqr_s),
	.process(),
    .fbit(sqr_fb),
    .skip(N-1), //Т.к. умножаются два числа с без целой части
	.rdy()
);	

wire ws;           //Поток коэффициента w
wire w_fbit;       //флаг выхода первого бита w

serial_streamer  #(
    .N(N)	    //Число бит входа
    ) ss_w (
    .rst(rst),          //Асинхронный сброс
    .clk(clk),          //Тактовый генератор
    .x(w),              //Вход
    .start(sqr_fb),      //Строб, старта. Выбран так, чтоб первый бит вышел одновременно с выходом возводителя в квадрат
    .y(ws),           //Очередной бит потока
    .fbit(w_fbit)         //Флаг того, что в y выходит первый бит нового числа
    );

reg sqr_s_z;   //поток sqr задержанный на 1 такт

always @(posedge clk, posedge rst)
    if(rst)
        sqr_s_z <= 0;
    else
        sqr_s_z <= sqr_s;

wire af_s;    //Поток выхода актиавционной функции
wire af_fbit; //Флаг выхода первого бита выхода активационной функции

wire ws_m;         //ws с учетом того, что в левой и правой параболах этого коэффициента нет
wire sqr_sm;       //sqr_s для всех, кроме центральной параболы. Для нее NOT sqr_s. конечно, было б не дурно еще 1 добавить, но вроде и так не плохо

assign sqr_sm = (wm) ? (sqr_s_z) : !sqr_s_z;
assign ws_m = ws&wm;

serial_subs sub_w(	
	.rst(rst), 		//Асинхронный сброс
	.clk(clk), 		//Тактовый генератор
	.a(ws_m),		//Слогаемое a
	.b(sqr_sm),		//Слогаемое b		
	.start(w_fbit),	//Синхронный сброс
	.c(af_s),   //Результат сложения
	.ovf()  //Флаг переноса
	);	


always @(posedge clk, posedge rst)
    if(rst)
        af_fbit <= 0;
    else
        af_fbit <= w_fbit;

assign fbit = af_fbit;
assign y = af_s;

endmodule
