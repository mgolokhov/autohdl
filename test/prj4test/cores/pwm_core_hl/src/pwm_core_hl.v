//***************************************ШИМ Генератор с ШИМ декодером******************************
//Авторы: Романов А.М., Киор С.В.
//		  Кафедра "Проблем управления" МИРЭА(ТУ), 2009 г.
//**************************************************************************************************//

module pwm_core_hl(
	input rst,							//Асинхронный сброс
	input clk,							//Тактовый генерато
	input [15:0] val_in,				//Скважность
	output h_out,  						//Выход на нижний транзитор
	output l_out,						//Выход на верхний транзитор
	output pwm_ready					//Флаг окончания периода ШИМ (для загрузки нового значения скважности)
	);
	
	parameter k=14;						//Кол-во бит ШИМ		  
	parameter pwm_deadzone=0;

	reg  [15:0] val_in_s;	   
    wire [16:0] val_in_s_dz;	
	reg  [15:0] val_in_st;	   
	
	always @(posedge clk, posedge rst)	//Перевод регистра val_in в новый частотный домен
	if(rst)
	val_in_s <= 0;
	else
	val_in_s <= val_in;   
	
	assign val_in_s_dz = (val_in_s[15]) ? {val_in_s[15],val_in_s} - pwm_deadzone : {val_in_s[15],val_in_s} + pwm_deadzone;	//Компенсация мертвой зоны в 0  
	
	always @(*)   //Проверка на превышение ограничения
		begin
			if (val_in_s_dz[16])
				begin 
					if (val_in_s_dz[15])
						val_in_st <= val_in_s_dz[15:0];
					else
						val_in_st <= 16'h8000;
				end							  
			else
				begin 
					if (val_in_s_dz[15])
						val_in_st <= 16'h7FFF;
					else
						val_in_st <= val_in_s_dz[15:0];
				end	
		end	
	
	 
	reg [k-1:0]val;						//Значение таймера при котором переключаются уровни Hi и Low
	reg [k-1:0]cnt;                       //Регистр таймера
	
	
	always @(posedge clk, posedge rst)
	if(rst)
		val <= 0;
	else							
		if(cnt == 0) 
			val <= (val_in_st[15:16-k])+(1<<(k-1));	  //Если предыдущий период ШИМ закончился загрузим новое значение 
												  //скважоности и переведем его из диапазона [-2^(k-1) 2^(k-1)-1] в [0 2^k-1]
			
    reg cnt_sign;
	
	always @(posedge clk, posedge rst)			  //Декриментирующийся таймер, с возможностью загрузки периода
	if(rst)
		{cnt_sign,cnt} <= 0;		
	else
		{cnt_sign,cnt} <= {cnt_sign,cnt} - 1; 
		
	wire [k-1:0]pwm_c;	
	assign pwm_c = (cnt_sign) ? ~cnt : cnt;
												  
	assign {h_out,l_out} = (val > pwm_c) ? 2'b10 : 2'b01; //Переключение уровней Hi и Low
	
	assign pwm_ready = (cnt==0);                   //За 2 такта выставляем наружу ready, чтобы когда его примут и выставят новое
	                                               //значенеи он записалось в близжайший период
	
	
endmodule
