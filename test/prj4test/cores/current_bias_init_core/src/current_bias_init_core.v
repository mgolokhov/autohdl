module current_bias_init_core(
	input rst, //Сброс
	input clk, //Тактовый генератор
	input start, //Запуск измерения токового смещения
	input [11:0]ia, //Вход с АЦП тока A
	input [11:0]ib,	//Вход с АЦП тока B
	input adc_rdy,  //Вход готовности АЦП
	output reg [11:0]ia_bias, //Смещение тока a
	output reg [11:0]ib_bias, //Смещение тока b
	output reg rdy);  //Флаг готовности
	
	
reg [19:0]ia_b;	 //Регистры используемые для накопления среднего значения
reg [19:0]ib_b;	 //Регистры используемые для накопления среднего значения

reg [10:0]timer;
reg [1:0]state;  //Флаг того, что идет процесс вычисления

always @(posedge rst, posedge clk)
	if(rst)
		begin 
			ia_bias <= 0;
			ib_bias <= 0;
			timer <= 0;
			rdy <=0;			
            ia_b <=0;				   
            ib_b <=0;				   
			state <= 0;
		end	 else
		if (timer)
			begin 
				if(adc_rdy)					//Таймер отсчитывает определенное кол-во срабатываний  АЦП
                    begin
    					timer<=timer-1;
                        ia_b <= ia_b+{ia[11],ia[11],ia[11],ia[11],ia[11],ia[11],ia[11],ia[11],ia}; //Интегрируем в ia_b значение тока ia
                        ib_b <= ib_b+{ib[11],ib[11],ib[11],ib[11],ib[11],ib[11],ib[11],ib[11],ib}; //Интегрируем в ib_b значение тока ib
                    end
				rdy<=0;	
			end	else
			begin 
                case(state)
                2'b00:  begin
						    if (start)
							    begin 
								    timer <= 2000;		//Если старт, то отсчитываем 1000 тактов АЦП, чтоб дождаться окончания переходного процесса по току
								    state <= 2'b01;
							    end	
						    rdy <= 0;
                        end
                2'b01:  begin
                           ia_b <= {ia[11],ia[11],ia[11],ia[11],ia[11],ia[11],ia[11],ia[11],ia}; //Выставляем в ia_b значение тока ia
                           ib_b <= {ib[11],ib[11],ib[11],ib[11],ib[11],ib[11],ib[11],ib[11],ib}; //Выставляем в ib_b значение тока ib
                           timer <= 255;    //Выставляем таймер на 255 итерации в течении которых накопим еще 255 значений тока
                           state <= 2'b10;     
                        end
                2'b10:  begin
                            ia_bias <= ia_b[19:8];     //Берем средние значения токов за последние 256 тактов                 
                            ib_bias <= ib_b[19:8];                      
                            state <= 2'b00;
                            rdy <= 1;
                        end 
                endcase
			end	
	
endmodule	
