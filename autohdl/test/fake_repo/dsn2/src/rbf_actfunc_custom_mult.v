//***********************************Активационная функция RBF - нейрона*********************************************
//Романов А.М. Кафедра "Проблемы управления" МИРЭА, 2010 г.
//ВАЖНО: x-b+b1, x-b-b1, x-b - для любого a*x[-1:1] окажутся в дипазоне от [-1:1], перед поступлением на умножители, т.к.
//сигмода всегда лежит [0 1]
//а вот x_arg может и не оказаться. Но для s [0 1] вроде как x_arg лежит [-2^bN 2^bN] (надо б еще потестить)
//*******************************************************************************************************************

module rbf_actfunc_custom_mult
	#(parameter  N=16, 			//Число бит входа и коэффициентов
      parameter  bN=2,          //Число бит целой части b,b1 и s  
      parameter  aN=4,           //Число бит целой части a0,a1
      parameter  cN = N+bN+aN  //длина умножителя кордика 
	)	
	(
	input rst,					//Асинхронный сброс
	input clk,					//Тактовый генератор
	input start,				//Строб старта
	input [N-1:0]x,				//Вход [-1 1]
	input [N-1:0]a0,			//Коэффициент a0=sqrt(w)*sqrt(1-exp(-0.5))/s
	input [N-1:0]a1,			//Коэффициент a1=sqrt(w)*sqrt((1-exp(-0.5))./s./(b1-s))
    input [N-1:0]b,             //параметр b - середина сигмоиды
    input [N-1:0]b1,            //параметр b1=s/(1-exp(-0.5))
    input [N-1:0]s,             //параметр s - сигма сигмоиды 
    input [N-1:0]w,             //весовой коэффициент [-1 1]
    input [1:0]func_type,       //Тип активационной функции 0 или 1 - обычная, 2 - левее купола высокий уровент, 3-правее купола высокий уровень
    
    output start_mult,   //Строб старта умножителя
    output reg [cN-1:0]mult_a,  //множитель а
    output reg [cN-1:0]mult_b,  //множитель b
    input [cN-1:0]mult_c, //результат умножения
    input mult_rdy,       //флаг готовности результата

	output reg [N-1:0]y,	   	        //Выход активационной функции в виде потока
	output reg rdy			    	//Флаг готовности
	);


reg [N+bN:0]dxb;        //x-b
reg [N+bN+1:0]dxb_s;    //|x-b|-s или x-b+b1, или x-b-b1

wire [bN-1:0]blow; //младшие знаки b
wire [bN-1:0]b1low; //младшие знаки b1
wire [bN:0]xhi;  //старшие биты x
wire [bN-1:0]slow; //младшие знаки s

assign blow  = 0;
assign b1low = 0;
assign slow =  0;
assign xhi   = (x[N-1]) ? -1 : 0;

//typedef enum logic[8:0] {  
parameter
	st_idle			= 9'b000000001,
	st_st1   		= 9'b000000010,
	st_st2   		= 9'b000000100,
	st_st3   		= 9'b000001000,
	st_st4   		= 9'b000010000,
	st_st5   		= 9'b000100000,
	st_st6   		= 9'b001000000,
	st_st7   		= 9'b010000000,
	st_st8   		= 9'b100000000
	;//} SelState;
	
	reg [8:0] /*SelState*/ state;						  

reg [1:0]x_pos;  //Положение x
//2'b00 - левее левой параболы или правее правой (т.е. в итоге результат будет равен 0)
//2'b01 - левая или правая парабола парабола y=(a1*(x-b+b1))^2;
//2'b10 - центральная парабола y=w-(a0*(x-b))^2
//2'b11 - левая часть у левой акт-функции и правая часть у правой (высокий уровень)
reg start_c; //запуск умножителя
assign start_mult = start_c;	

reg start_c_sel;  //Запуск селектора коэффициентов

reg [N+bN-1:0]x_arg;  //Значение x с учетом смещения на b, b1 или -b1
reg [N-1:0]a;    //Значение коэффициента a
reg wm;          //Флаг включающий или отключающий смещение на 1   (включено только у центральной параболы)


always @(posedge clk,posedge rst)
    if(rst)
    begin
        dxb <= 0;
        dxb_s <= 0;
        x_pos <= 2'b00;
        state <= st_idle;
        start_c_sel <= 0;
        start_c <=0;
        mult_a <= 0;
        mult_b <= 0;
        rdy <=0;
        y<=0;        
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
                    rdy<=0;
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
                    state <= st_st5;    
                    start_c_sel <= 1;  //Запускаем селектор коэффициентов
                end
            st_st5:
                begin
                   start_c_sel <= 0;  //ждем такт пока работает селектор
                   state <= st_st6;
                end
            st_st6:
                begin
                  mult_a[cN-1:bN+aN] <=  a;  //в первый множитель пишем a
                  mult_a[aN+bN-1:0] <= 0;
                  mult_b[cN-1:aN] <= x_arg;
                  mult_b[aN-1:0] <= 0;
                  start_c <= 1;  //запускаем умножитель
                  state <= st_st7;
                end
            st_st7:
                begin
                    if(mult_rdy)
                        begin
                            mult_a[cN-1:aN+bN] <= mult_c[N-1:0];  //В оба множителя пишем mult_c
                            mult_b[cN-1:aN+bN] <= mult_c[N-1:0];
                            mult_a[aN+bN-1:0] <= 0;    //В младшую часть пишем 0.
                            mult_b[aN+bN-1:0] <= 0;    //В младшую часть пишем 0.
                            start_c <= 1;           //Запускаем умножитель
                            state <= st_st8;
                        end else
                            start_c <= 0;
                end
            st_st8:
                begin
                    if(mult_rdy)
                        begin
                            case ({wm,w[N-1]})
                               2'b00: y<=  mult_c[cN-1:aN+bN];
                               2'b01: y<= -mult_c[cN-1:aN+bN];
                               2'b10: y<=w-mult_c[cN-1:aN+bN];   //Переполнения не возникает из-за свойств сигмоиды (она всегда лежит [0 w])
                               2'b11: y<=w+mult_c[cN-1:aN+bN];   //Переполнения не возникает из-за свойств сигмоиды (она всегда лежит [0 w])
                               default : y <= 0;
                            endcase
                            rdy <= 1;
                            state <= st_idle;                                
                        end else
                            start_c <= 0;                        
                end
                        
        endcase

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

endmodule
