`default_nettype none

module ssi
#(parameter prescaler = 500, ssi_stop = 52, dim = 32 )
(
    input clk,				// Клок 50 Mhz
    input rst,				// Ресет активный высокий
    output reg ssi_clk_out,			// Выход на SSI клок
    input  ssi_data_in,			// Вход данных от SSI
    input  read_in,			// Строб запроса датчика
    output reg [dim-1:0] data_out,		// Выход данных
    output reg data_ready			// Готовность данных
) ;


reg [31:0] scale;
reg ping;		// Строб 100 КГц
reg presc_ena;

always @(posedge clk, posedge rst)
if(rst)
begin
  scale <= 0;
  ping <= 0;
end
else
begin
  if(presc_ena)
    if(scale == 0)
    begin
      scale <= prescaler;
      ping <= 1;
    end
    else
    begin
      scale <= scale - 1;
      ping <= 0;
    end
  else
    begin
      scale <= prescaler;
      ping <= 0;
    end
end


reg ssi_data;

always @(posedge clk, posedge rst)
if(rst)
  begin
    ssi_data <= 0;
  end
else
  begin
    ssi_data <= ssi_data_in;
  end
    


reg [7:0] ssi_a;

parameter ssi_wait = 0;
	  
reg [dim-1:0] ssi_value;

always @(posedge clk, posedge rst)
if(rst)
  begin
    ssi_a <= ssi_wait;
    ssi_clk_out <= 1;
    presc_ena <= 0;
    ssi_value <= 0;
    data_out <= 0;
    data_ready <= 0;
  end
else
begin
  case (ssi_a)
    ssi_wait: if(read_in)
    begin
      ssi_a <= ssi_a + 1;
      ssi_clk_out <= 0;
      presc_ena <= 1;
      ssi_value <= 0;
    end else data_ready <= 0;
/* else
    begin
      ssi_clk_out <= 1;
      presc_ena <= 0;
    end
*/
    ssi_stop:
    begin
      //data_out <= data_out + 1;
      data_out <= ssi_value;
      data_ready <= 1;
      ssi_clk_out <= 1;
      presc_ena <= 0;
      ssi_a <= ssi_wait;
    end
    default:
      if(ping)
      begin
	ssi_a <= ssi_a + 1;
	if(ssi_a[0])
	  begin // Low
	    ssi_clk_out <= 1;
	  end
	else
	  begin
	    ssi_clk_out <= 0;
	    ssi_value <= {ssi_value[dim-2:0],ssi_data};
	  end
      end
  endcase
end



endmodule