module crc_6(
	input [7:0]data,
	input [5:0]crc,
	output [5:0]new_crc
	);
	
assign new_crc[0] = data[6] ^ data[5] ^ data[0] ^ crc[3] ^ crc[4];
assign new_crc[1] = data[7] ^ data[5] ^ data[1] ^ crc[0] ^ crc[3] ^ crc[5];
assign new_crc[2] = data[6] ^ data[2] ^ data[1] ^ crc[0] ^ crc[4];
assign new_crc[3] = data[7] ^ data[3] ^ data[2] ^ crc[0] ^ crc[1] ^ crc[5];
assign new_crc[4] = data[4] ^ data[3] ^ data[1] ^ crc[2];
assign new_crc[5] = data[5] ^ data[4] ^ data[2] ^ crc[3];
	
endmodule	