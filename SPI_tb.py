from myhdl import Signal, intbv,always, instance, delay, block, StopSimulation
from SPI import SPIMaster, SPISlave

@block
def spi_testbench():
	clk = Signal(bool(0))
	mosi = Signal(bool(0))
	miso = Signal(bool(0))
	sclk = Signal(bool(0))
	cs = Signal(bool(1))
	data_in_master = Signal(intbv(0xA5)[8:])
	data_out_master = Signal(intbv(0)[8:])
	data_in_slave = Signal(intbv(0x5A)[8:])
	data_out_slave = Signal(intbv(0)[8:])
	start = Signal(bool(0))
	
	master = SPIMaster(mosi, miso, sclk, cs, data_in_master, data_out_master, clk, start)
	slave = SPISlave(miso, mosi, sclk, cs, data_in_slave, data_out_slave)
	
	@always(delay(10))
	def clkgen():
		clk.next = not clk
		
	@instance
	def stimulus():
		print("Starting SPI Test...")
		yield delay(20)
		
		
		start.next = True
		yield clk.posedge
		start.next = False
		
		# Wait for the trasaction to complete
		while not cs:
			yield clk.posedge
			
		yield delay(10)
			
		print(f"Master Sent: {hex(data_in_master)}, Slave Received: {hex(int(data_out_slave))}")
		print(f"Slave Sent: {hex(data_in_slave)}, Master Received: {hex(int(data_out_master))}")
		
		assert int(data_in_master) == int(data_out_slave), "Master to Slave data mismatch"
		assert int(data_in_slave) == int(data_out_master), "Slave to Master data mismatch"
		
		print("SPI Test Passed")
		raise StopSimulation()
		
	return master, slave, clkgen, stimulus
	
#Run the testbench with pytest compatibility
def test_spi():
	tb = spi_testbench()
	tb.config_sim(trace=True)
	tb.run_sim()
