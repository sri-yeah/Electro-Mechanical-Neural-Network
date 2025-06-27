import serial 
import time

def send_weights(weights):
	# Set up 
	ser = serial.Serial("/dev/serial0", 9600, timeout=1)
	time.sleep(2)
	
	address_counter = 0
	data_key = '000'
	override = '0'
	for weight in weights:
		if weight == -1:
			data_key = '000'
		if weight == -0.3:
			data_key = '001'
		if weight == 0:
			data_key = '010'
		if weight == 0.5:
			data_key = '011'
		if weight == 1:
			data_key = '100'
		
		address = f"{address_counter:03b}"
		message = address + data_key + override 
		address_counter += 1
		print(f'Sending message: {message}')
		ser.write(message.encode('utf-8'))
		time.sleep(2)
	print('Sent all messages, closing')
	ser.close()
