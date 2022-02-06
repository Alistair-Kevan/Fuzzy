import asyncio
import serial_asyncio
import websockets

# Try this port. If I get nothing printing out, try '/dev/ttyAMA0'
#SERIAL_PORT = '/dev/ttyACM0' 
SERIAL_PORT = '/dev/ttyUSB0'
BAUDRATE = 9600

class SerialConnection(asyncio.Protocol):

    data_buffer = ''

    # Example of co-routine that sends data to a server
    async def send_data(self, data):
        async with websockets.connect(os.getenv('PUBLISH_SOCKET_LINK')) as ws:
            dataline = data
            if dataline != '':
                await ws.send(dataline)

    # Built-in protocol method provided by pyserial-asyncio
    def data_received(self, data):
        # Gather the data in a chunk until it's ready to send
        self.data_buffer += data.decode('utf-8')
        if '\r\n' in self.data_buffer:
            data_to_send = self.data_buffer.strip('\r\n')
            print(data_to_send)
            
           # Reset the data_buffer!
            self.data_buffer = ''
            
            '''
            At this point, you can make an HTTP Request with this data or use websockets!
            '''
            # asyncio.get_event_loop().create_task(self.send_data(data_to_send))

def record(path = None):
    # Boiler-plate for getting the pyserial-asyncio goodness to work
    loop = asyncio.get_event_loop()
    serial_connection = serial_asyncio.create_serial_connection(loop, SerialConnection, SERIAL_PORT, baudrate=BAUDRATE)
    try:
        loop.run_until_complete(serial_connection)
        loop.run_forever()
    finally:
        loop.close()

if __name__ == '__main__':
    record()


