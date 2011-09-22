//***************************Модуль реализует нейрон с поли-сигамаидальной передаточной функцией*********************
//На вход подается width*3 бит. из которых старшие 3*width бит равны знаковому						  
//
//Романов А.М. Кафедра "Проблемы управления" МИРЭА, 2010 г.
//*******************************************************************************************************************

module serial_neuron_core
	#(
	parameter N=2,			//Число входов
	parameter width=8,		//Число бит входных значений
	parameter skip_width = log2(width),																		   
	parameter skip_size = width 	//Биты пропускаемые на входе активационной функции
	)(								//По умолчанию пропускаем младшие width шагов. По сути это кол-во бит дробной части + 1.
		input rst,				//Асинхронный сброс
		input clk,				//Тактовый генератор
		input start,			//Флаг начала расчета
		input [N-1:0]inp,		//Входные значения
		input [N-1:0]w,			//Коэффициенты весов
		output reg [2*width-skip_size-1:0]out, //Выходное значение
		output reg rdy				//Флаг того, что вычисления окончены
	);		   

function integer log2;			//Функция выисления логорифма по основанию 2
  input integer value;
  begin
    for (log2=0; value>0; log2=log2+1)
      value = value>>1;
  end
endfunction	
	
	
wire [N-1:0]m_out;  //Выход умножителей на вес после умножения	

//Добавление умножителей на вес
generate	
	genvar i;
	for (i = 0; i<N; i=i+1)
	begin: WeightMult
		serial_mult #(
			.N(width))
		WSerialMult (
			.rst(rst),
			.clk(clk),
			.start(start),
			.a(inp[i]),
			.b(w[i]),
			.c(m_out[i]),
			.process(),
			.rdy()
		);			 
	end		 
endgenerate	 		

reg start_sum;	 //Строб старта сумматора - задержанный на такт строб старта умножителей. Т.к. первый бит
				 //на выходе умножителей появиться через 1 такт после начала умножения
always @(posedge rst, posedge clk)
	if(rst)
		start_sum <= 0;
	else
		start_sum <= start;
		
wire s_out;	//Выход сумматора
		
//Добавление N входового параллельного сумматора		
serial_summ_n #(  
	.N(N))
InputSum (
	.rst(rst),
	.clk(clk),
	.start(start_sum),
	.sumand(m_out),
	.result(s_out),
	.ovf()
);			   


wire x2_out; 	//Выход x^2
wire  start_x2;  //Строб запуска умножителя x^2
reg  [skip_width:0]skip_count;  //Кол-во шагов которые надо пропустить, дабы обеспечить дробную часть числа

always @(posedge rst, posedge clk) //Умножитель запускается на следующем такте после сумматора(т.е. с первым выходным битом суммы)
	if(rst)		
		skip_count <= -1;
	else	
		begin
			if(start_sum)				//Если пришел строб запуска, то устанавливаем число бит которые надо пропустить
				skip_count <= skip_size;
			if(~skip_count[skip_width])	 //Если skip_count положительный то вычитаем 1	
				skip_count <= skip_count - 1; 	//Т.е. если skip_size = 1, то при приходе start_sum, skip_count становится равным 1
		end										//далее 1 такт он будет 1,(т.е. один такт будет пропущен). Через 2 такта он стане равным 0
												//и будет сформирован строб start_x2, как раз параллельно со вторым битом на выходе сумматора
assign start_x2 = (skip_count == 0);		
		
serial_mult #(	//Умножитель x^2
	.N(width))
	x2_mult (
	.rst(rst),
	.clk(clk),
	.start(start_x2),
	.a(s_out),
	.b(s_out),
	.c(x2_out),
	.process(),
	.rdy()
);			 

wire x3_out; 	//Выход x^2
reg  start_x3;  //Строб запуска умножителя x^2
reg  z_x;		//х-задержанный на 1 такт

always @(posedge rst, posedge clk) //Умножитель запускается на следующем такте после сумматора(т.е. с первым выходным битом суммы)
	if(rst)
		start_x3 <= 0;
	else
		start_x3 <= start_x2;

always @(posedge rst, posedge clk)	//Задерживаем x на 1 такт
	if(rst)
		z_x <= 0;
	else
		z_x <= s_out;
		
serial_mult #(					     //Умножитель возводящий в x^3
	.N(width))
	x3_mult (
	.rst(rst),
	.clk(clk),
	.start(start_x3),
	.a(z_x),
	.b(x2_out),
	.c(x3_out),
	.process(),
	.rdy()
);			 

wire x15;

serial_summ one_and_half_x_sum (	//Сумматоры вычисляющий 1.5x. Т.к. из результата мы потом все равно возьмем только младшие width бит 
	.rst(rst),						//можно не волноваться за тот случай, когда s_out уже закончился,а z_x еще нет. Т.к. даже в случае 2 нейронов
	.clk(clk),						//мы имеем не менее 2*width+1 бит выходящий из сумматора
	.a(z_x),
	.b(s_out),
	.start(start_x3),
	.c(x15),
	.ovf(ovf)
);		 

reg z_x15;	//1.5 x задержанные на 1 такт. Делается это потому, что x^3/2 появится только на следующем шаге (ну т.е. 1 бит x3 на следует опустить)
			//при этом в связи с тем, что умножитель после 2*width бит пихает все остальные биты - знаковыми, то опасения за то, что старший бит
			//x^3/2 будет неправильным вроде, как не обоснованы:)
			
reg pr_start_subs; //Т.к. start_subs задержан на 2 такта относительно start_x3(чтоб начать вычитать со второго бита x^2), то ему нужна дополнительная задержка на такт			
reg start_subs;    //Строб запуска выходного вычитатора

always @(posedge rst, posedge clk)
	if(rst)
		z_x15 <= 0;
	else
		z_x15 <= x15;
		
always @(posedge rst, posedge clk)
	if(rst)
		begin 
			pr_start_subs <= 0;
			start_subs <= 0;
		end else
		begin 				
			pr_start_subs <= start_x3;  		//Формирование строба запуска вычитатора задержкой строба startx3 на два такта
			start_subs <= pr_start_subs;
		end	
		
wire non_sat_out;					  //Выход нейрона, не ограниченный от -1 до 1		
		
serial_subs final_substract (	      //Выходной вычитатор, реализующий 1.5x-0.5x^3
	.rst(rst),						
	.clk(clk),						
	.a(z_x15),
	.b(x3_out),
	.start(start_subs),
	.c(non_sat_out),
	.ovf()
);		 

//Формирование выхода	
parameter max_out_buf= 3*width-skip_size-1;	//Максимальный индекс выходного буффера

reg [max_out_buf:0]out_buf; //Буффер в который складывается выход
reg out_rdy;			  //Флаг того, что все биты выходного числа пришли

reg last_bit;			//Флаг того, что пришел последний бит

always @(posedge rst, posedge clk)
	if(rst)		  
		begin 
			{out_buf,out_rdy} <= 1;
			last_bit <= 0;
		end	
	else
		if(start_subs)							   
			begin 
				{out_buf[max_out_buf-1:0],out_rdy} <= 0; //Обнуляем входной буффер
				out_buf[max_out_buf] <= 1;			 //Выставляем в старший бит 1, для того, чтобы когда она сдвинится в out_rdy мы знали, что пора закончить
				last_bit <= 0;
			end	
		else		 
			if(~out_rdy)
				begin 
        			{out_buf,out_rdy} <= {non_sat_out,out_buf};  //На каждом такте вдвигаем очередной бит выхода вычитатора в out_buf
															//как только положенная в него в самом начале еденица вдвинится в out_rdy
															//можно считать что все биты результата получены.						 
					if(out_buf[0])    	//За такт до конца выставляем последний бит. Это означает, что со следующего тактка out_buf содержит результат
						last_bit <= 1;
					else
						last_bit <= 0;
				end else
					last_bit <= 0;
															

wire comp_1;  //Выход компоратора выхода сумматор  1
wire comp_m1; //Выход компоратора выхода сумматор -1

reg  gen_1;	  //Очередной бит опроной для компоратора  1
reg  gen_m1;  //Очередной бит опроной для компоратора -1	

parameter gen_width = log2(3*width-skip_size)+1;  //Ширина счетчика для формирования опорного выхода																		   
parameter gen_chng_bit = 2*width-skip_size+1;	//Значения счетчика по которому мы меняем значения gen_1 и gen_m1(т.е. после него начинаем выдавать на выход знаковые биты)
												//Вычеслен имперически
reg [gen_width:0]gen_counter; //Cчетчик опоры

always @(posedge rst, posedge clk)
	if(rst)
		  gen_counter <= -1;
	else begin 
			if(start_x2)                  		//Паралельно с запуском вычитаторов начинаем обратный отсчет счетчика опоры. При этом в момент start_x2 gen_1 и gen_m1 имееют значения полученные по ресету или после предыдущего формирования опоры(по счетчику со значением 0))
				gen_counter <= 3*width-skip_size-2;	//Значение -2 получено имперически. Просто посмотрел на примерах сколько надо, чтоб в момент формирования последнего бит счетчик был равен 0
			if(~gen_counter[gen_width])			//Если есть чего считать ведем обратный отсчет.
				gen_counter <= gen_counter - 1;
		 end	
		 
always @(posedge rst, posedge clk)
	if(rst)
		begin 
			gen_1 <= 1;							//Инициализируем младший бит +1
			gen_m1 <= 0;						//Инициализируем младший бит -1
		end	else
		begin		   
			if(~gen_counter[gen_width])        	//Если счетчик считает
				begin 
					if(gen_counter[gen_width-1:0]==0) //Если счетчик равен 0, то инициализируем переменные аналогично ресету
						begin 						  //Так как именно эти значения будут в момент следующего прихода start_x2
							gen_1  <= 1;
							gen_m1 <= 0;
						end	else
					if(gen_counter[gen_width-1:0]==gen_chng_bit)	//После того как передали все младшие биты начинаем передавать знаковые
						begin 
							gen_1  <= 0;
							gen_m1 <= 1;
						end	
						
				end	
		end	
			

serial_subs x_comparator_1(	//Компаратор сигнала x с 1      
	.rst(rst),						
	.clk(clk),						
	.a(s_out),
	.b(gen_1),
	.start(start_x2),
	.c(comp_1),
	.ovf()
);		 

serial_subs x_comparator_m1( //Компаратор сигнала x с -1      
	.rst(rst),						
	.clk(clk),						
	.a(s_out),
	.b(gen_m1),
	.start(start_x2),
	.c(comp_m1),
	.ovf()
);		 

reg [1:0]x_sat_state;     //состояние проверки ограничения выхода нейрона задержанное на 1 такт 																 																
reg [1:0]x_sat_state_z;   //состояние проверки ограничения выхода нейрона задержанное на 2 такт
reg [1:0]x_sat_state_2z;  //состояние проверки ограничения выхода нейрона задержанное на 3 такт 																
//Задержка нужна для того, чтобы параллельно с последним битом на выходе активационной функциии получить знаки с компораторов(т.е. по факту узнать надо ли ограничивать выход)
//2'b10 надо ограничить -1
//2'b00 не надо ограничивать
//2'b01 надо ограничить +1	

always @(posedge rst, posedge clk)
	if(rst)
		x_sat_state <= 2'b00;
	else
		x_sat_state <= {comp_m1,~comp_1};  //Если comp_m1 = 1(для последнего знака) , значит разность x-(-1) отрицательна, значит x <- 1. Т.е. число следует ограничивать до -1
		//Если comp_1  = 0(для последнего знака) , значит разность x-(1)  положительная, значит x > 1. Т.е. число следует ограничивать до  1

always @(posedge rst, posedge clk)		//Задержка x_sat_state на двa такта
	if(rst)
		begin 
			x_sat_state_z  <= 2'b00;
			x_sat_state_2z <= 2'b00;
		end	else
		begin 
			x_sat_state_z  <= x_sat_state;
			x_sat_state_2z <= x_sat_state_z;
		end										 
		
		
//Фомирование выходного значения		
always @(posedge rst, posedge clk)
	if(rst)
		out <= 0;
	else				 
		if(last_bit)
			case (x_sat_state_2z)	
				2'b00 : out <= out_buf[2*width-skip_size-1:0];	//Если x находился в диапазоне [-1 1], то выход равен выходу активационной функции
				2'b01 : begin 									//Если x > 1 , то выход равен 1
							out[2*width-skip_size-1:skip_size-1]   <=  0;	//Т.е старшие биты равны 0
							out[skip_size-2:0] <= -1;						//А все младшие равны 1
						end
				2'b10 : begin 									//Если x < -1 , то выход равен -1
							out[2*width-skip_size-1:skip_size-1]   <= -1; //Т.е старшие биты равны 1
							out[skip_size-2:0] <= 0;					  //А все младшие равны 0
						end								   
				2'b11 :  out[2*width-skip_size-1:0] <= 0; //В случае x<-1 и x>1 выход равен 0, т.к. при нормальном функционировании такого выхода не бывает
				default: out[2*width-skip_size-1:0] <= 0; //Во всех остальных случаях (типа x и z состояний выход также равен 0)
		    endcase
			
//Флаг готовности - по сути флаг last_bit сдвинутый во времени на такт			
always @(posedge rst, posedge clk)
	if(rst)
		rdy <=0;
	else
		rdy <= last_bit;
		
endmodule