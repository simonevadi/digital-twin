import asyncio
import os
import csv

class ClientProtocol(asyncio.Protocol):
    """
    Implementation of the asyncio.Protocol for the client.

    Args:
        exports_list (List[str]): List of data exports to transmit.
        file_path (str): Path to the directory containing temporary files.
        prefix (str): Prefix appended by raypyng to the simulated device
    """

    def __init__(self, exports_list, file_path, prefix):
        self.exports_list = exports_list
        self.file_path = file_path
        self.filename = None
        self.prefix = prefix
        self.received_data = ''
        self.finished = asyncio.Future()  # Future to signal when the connection is closed

    def connection_made(self, transport):
        """
        Called when a connection is made.

        Args:
            transport (asyncio.BaseTransport): The transport representing the connection.
        """
        self.transport = transport
        self.loop = asyncio.get_event_loop()

        with open(os.path.join(self.file_path, 'tmp.rml'), 'rb') as file:
            file_content = file.read()

        data_to_send = f"{','.join(self.exports_list)}|||{file_content.decode('utf-8')}"
        self.transport.write(data_to_send.encode('utf-8'))

        files = os.listdir(self.file_path)
        for file in files:
            if file.endswith(".dat") or file.endswith(".csv"):
                file_path = os.path.join(self.file_path, file)
                os.remove(file_path)

    def data_received(self, data):
        """
        Called when some data is received.

        This method is invoked whenever new data is received over the network connection. The received data is checked
        for a specific termination string, "|ENDOFTRANSMISSION|", indicating the end of a data transmission. If the
        termination string is found, the received data is processed to extract filenames and corresponding file contents.
        These are then written to CSV files in the specified file path. If the filename matches the current instance's
        filename attribute, the CSV file is opened in append mode; otherwise, a new file is created.

        Args:
            data (bytes): The received data.
        """
        if 'IndexError' in data.decode('utf-8'):
            raise ValueError('Not enough rays for the simulations\nCtrl+c twice, RE.abort()')
        elif 'SimulationError' in data.decode('utf-8'):
            raise ValueError('Simulations Failed for unknown reason')
        elif "|ENDOFTRANSMISSION|" in data.decode('utf-8'):
            # Extract and process the received data
            self.received_data += (data.decode('utf-8'))
            self.received_data = self.received_data.replace("|ENDOFTRANSMISSION|", "")
            self.received_data = self.received_data[0:-3]

            received_transmission_list = self.received_data.split('|||')

            # Process each filename and file content pair
            for i in range(0, len(received_transmission_list), 2):
                filename = received_transmission_list[i]
                file_content = received_transmission_list[i + 1]

                # Determine whether to open the file in append or write mode
                if filename == self.filename:
                    open_file_mode = 'a'
                else:
                    open_file_mode = 'w'

                # Construct the save path and write the file content to a CSV file
                save_path = os.path.join(self.file_path, filename)
                with open(save_path, open_file_mode, newline='') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    data_lines = file_content.splitlines()
                    for line in data_lines:
                        csvwriter.writerow(line.split(','))

                # Update the current filename attribute
                self.filename = filename

            # Signal completion when data is processed
            self.finished.set_result(True)
        else:
            # Continue accumulating data if the termination string is not yet received
            self.received_data += (data.decode('utf-8'))


    def connection_lost(self, exc):
        """
        Called when the connection is lost.

        Args:
            exc (Exception): Exception indicating the reason for the connection loss.
        """
        print("Connection lost:", exc)

async def run_main_protocol(transport, protocol):
    """
    Main coroutine for running the protocol.

    Args:
        transport (asyncio.BaseTransport): The transport representing the connection.
        protocol (ClientProtocol): The client protocol instance.
    """
    try:
        await protocol.finished

    except KeyboardInterrupt:
        pass
    finally:
        pass 

async def run_asyncio_client(ip, port, prefix, exports_list, file_path):
    """
    Main coroutine for running the asyncio client.

    Args:
        ip (str): IP address of the server.
        port (int): Port number to connect to.
        prefix (str): Prefix for the connection.
        exports_list (List[str]): List of data exports to transmit.
        file_path (str): Path to the directory containing temporary files.
    """
    loop = asyncio.get_event_loop()
    transport, protocol = await loop.create_connection(lambda: ClientProtocol(exports_list, file_path, prefix), ip, port)
    # Create tasks for the main coroutine and waiting for protocol.finished
    main_task = asyncio.create_task(run_main_protocol(transport, protocol))

    # Wait for both tasks to complete
    await asyncio.gather(main_task, protocol.finished)
    return True
