module cmi_single_timeslot_generator(
	input rst,					//Асинхронный сброс
	input clk,					//Тактовый генератор
	input [15:0]width,			//Ширина временного слота в тактах генератора
	input reload,				//Строб обозночающий перезагрузку счетчика отправленной телеметрии
	input [23:0]cmi_count,		//Значение, которое нужно загрузчить в счетчик телметрии при поднятии строба reload
	output  marker_st 			//Строб на начало нового временного слота
	);

reg [16:0]timeslot_cnt;		//Cчетчик времени между временными слотами
reg [23:0]cmi_cnt;		//Счетчик ушедшей телеметрии

always @(posedge rst or posedge clk)
	if(rst)
		timeslot_cnt <= 0;
	else
		begin 
			if(cmi_cnt!=0)
				timeslot_cnt <= timeslot_cnt-1;		//Если мы еще не все отправили, то ведем обратный отсчем
			if(timeslot_cnt[16])
				timeslot_cnt <= {1'b0,width};		//Если досчитали до -1, то снова делае ширину width
		end																							   

assign marker_st = timeslot_cnt[16];
		
always @(posedge rst or posedge clk)
	if(rst)
		cmi_cnt<=0;
	else
		if(reload)                     		//Если строб reload, то загружаем новое значение в счетчик
			cmi_cnt <= cmi_count;
		else
			if(marker_st)						//Если пришел строб отправки телеметрии, дикрементируем счетчик
				cmi_cnt <= cmi_cnt - 1;
	
endmodule	
