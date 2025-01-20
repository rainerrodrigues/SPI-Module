from myhdl import block, always, instance, Signal, intbv, delay, StopStimulation

@block
def SPIMaster(mosi, miso, sclk, cs, data_in, data_out, clk, start, bit_count=8):
	"""
	SPI Master module
	
	mosi		- Master Out Slave In
	miso		- Master In Slave Out
	sclk		- Serial Clock
	cs		- Chip Select (Active low)
	data_in	- Data to send
	data_out	- Data to be received
	clk		- System clock
	start		- Start transaction signal
	bit_count	- Number of bits per transaction
	"""
	
	shift_reg = Signal(intbv(0)[bit_count:])
	bit_idx = Signal(intbv(0,min = 0,max=bit_count))
	busy = Signal(bool(0))
	
	@always(clk.posedge)
	def master_logic():
		if start and not busy:
			cs.next = 0 # Activate chip select
			shift_reg.next = data_in
			bit_idx.next = 0
			busy.next = True
		elif busy:
			if bit_idx < bit_count:
				sclk.next = not sclk # Toggle clock
				if sclk: # Capture on rising edge
					data_out.next[bit_idx] = miso
					mosi.next = shift_reg[bit_count - 1]
					shift_reg.next = shift_reg << 1
					bit_idx.next = bit_idx + 1
			else:
				cs.next = 1 #Deactivate Chip Select
				busy.next = False
					
	return master_logic
	
	
@block
def SPISlave(miso, mosi, sclk, cs, data_in, data_out, bit_count=8):
	"""
	SPI Slave module
	
	miso		- Master In Slave Out
	mosi		- Master Out Slave In
	sclk		- Serial Clock
	cs		- Chip Select
	data_in	- Data to send
	data_out	- Data received
	bit_count 	- Number of bits per transaction
	"""
	
	shift_reg = Signal(intbv(0)[bit_count:])
	bit_idx = Signal(intbv(0, min=o, max=bit_count))
	
	@always(sclk.posedge)
	def slave_logic():
		if not cs:
			data_out.next[bit_idx] = mosi
			miso.next = shift_reg[bit_count - 1]
			shift_reg.next = shift_reg << 1
			shift_reg.next[0] = data_in[bit_idx]
			bit_idx.next = bit_idx + 1
		else:
			bit_idx.next = 0
			
	return slave_logic
