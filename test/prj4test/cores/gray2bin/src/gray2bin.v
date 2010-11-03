`default_nettype none
module gray2bin(
	input clk,				// Клок 50 Mhz
	input rst,				// Ресет активный высокий
	input  read_in,			// Строб запроса датчика
	input  [31:0] gray_in,
	output reg [31:0] data_out,		// Выход данных
	output reg data_ready			// Готовность данных
	) ;
	
	
	wire [31:0] ww;
	
	
	assign ww[24] = 1'b0   ^ (gray_in[24]);
	assign ww[23] = ww[24] ^ (gray_in[23]);
	assign ww[22] = ww[23] ^ (gray_in[22]);
	assign ww[21] = ww[22] ^ (gray_in[21]);
	assign ww[20] = ww[21] ^ (gray_in[20]);
	assign ww[19] = ww[20] ^ (gray_in[19]);
	assign ww[18] = ww[19] ^ (gray_in[18]);
	assign ww[17] = ww[18] ^ (gray_in[17]);
	assign ww[16] = ww[17] ^ (gray_in[16]);
	assign ww[15] = ww[16] ^ (gray_in[15]);
	assign ww[14] = ww[15] ^ (gray_in[14]);
	assign ww[13] = ww[14] ^ (gray_in[13]);
	assign ww[12] = ww[13] ^ (gray_in[12]);
	assign ww[11] = ww[12] ^ (gray_in[11]);
	assign ww[10] = ww[11] ^ (gray_in[10]);
	assign ww[09] = ww[10] ^ (gray_in[09]);
	assign ww[08] = ww[09] ^ (gray_in[08]);
	assign ww[07] = ww[08] ^ (gray_in[07]);
	assign ww[06] = ww[07] ^ (gray_in[06]);
	assign ww[05] = ww[06] ^ (gray_in[05]);
	assign ww[04] = ww[05] ^ (gray_in[04]);
	assign ww[03] = ww[04] ^ (gray_in[03]);
	assign ww[02] = ww[03] ^ (gray_in[02]);
	assign ww[01] = ww[02] ^ (gray_in[01]);
	assign ww[00] = ww[01] ^ (gray_in[00]);
	

	
	always @(posedge clk, posedge rst)
		if(rst)
			begin
				data_out <= 0;
				data_ready <= 0;
			end
		else
			if(read_in)
				begin
					data_out <= ww;
					data_ready <= 1;
				end
			else
				data_ready <= 0;

	
endmodule

