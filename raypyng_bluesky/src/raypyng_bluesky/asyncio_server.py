import asyncio
import logging
import os
from typing import List

from raypyng.runner import RayUIRunner, RayUIAPI
from raypyng.postprocessing import PostProcess

def configure_logging(tmp_folder: str) -> None:
    """
    Configures logging to a file in the specified temporary folder.

    Args:
        tmp_folder (str): Path to the temporary folder.
    """
    log_file_path = os.path.join(tmp_folder, 'server_log.txt')
    logging.basicConfig(filename=log_file_path, level=logging.INFO, format='[%(asctime)s] %(message)s')

def log_message(message: str) -> None:
    """
    Logs a message with a timestamp.

    Args:
        message (str): The message to log.
    """
    logging.info(message)

def create_temp_folder(tmp_folder: str) -> None:
    """
    Creates the specified temporary folder if it doesn't exist.

    Args:
        tmp_folder (str): Path to the temporary folder.
    """
    if not os.path.exists(tmp_folder):
        os.makedirs(tmp_folder)

def save_received_file(file_content: str, tmp_folder: str) -> None:
    """
    Saves received file content to a file in the specified temporary folder.

    Args:
        file_content (str): The content of the received file.
        tmp_folder (str): Path to the temporary folder.
    """
    beamline_path = os.path.join(tmp_folder, 'beamline.rml')
    with open(beamline_path, 'w') as file:
        file.write(file_content)
    log_message(f"Data saved in {beamline_path}")

def perform_simulation(export_list: List[str], tmp_folder: str, ray_path=None) -> bool:
    """
    Performs simulation using Raypyng.

    Args:
        export_list (List[str]): List of objects to export during simulation.
        tmp_folder (str): Path to the temporary folder for storing simulation results.
        ray_path (str, optional): Path to Raypyng executable. Defaults to None.

    Returns:
        bool: True if the simulation is successful, False otherwise.
    """
    log_message("Starting Simulations")
    try:
        r = RayUIRunner(ray_path=ray_path, hide=True)
        a = RayUIAPI(r)
        r.run()
        rml_file_path = os.path.join(tmp_folder, 'beamline.rml')
        log_message(f'Loading rml_file_path {rml_file_path}')
        a.load(rml_file_path)
        log_message('File loaded')
        a.trace(a.trace(analyze=True))
        log_message('File traced')
        for obj in export_list:
            log_message(f'Exporting obj: {obj} in folder: {tmp_folder}')
            a.export(obj, "RawRaysOutgoing", tmp_folder, '')
        a.save(rml_file_path)
        a.quit()
        log_message(f"Simulations done")
        return True
    except Exception as e:
        log_message('Simulations failed. {e}') 
        return False

def postprocess_simulation(export_list: List[str], tmp_folder_path: str, rml_filename: str) -> bool:
    """
    Performs post-processing on the simulation results.

    Args:
        export_list (List[str]): List of objects exported during simulation.
        tmp_folder_path (str): Path to the temporary folder containing simulation results.
        rml_filename (str): Name of the RML file used in the simulation.

    Returns:
        bool: True if post-processing is successful, False otherwise.
    """
    log_message("Starting to Postprocess Data")
    try:
        for exp in export_list:
            pp = PostProcess()
            pp.postprocess_RawRays(
                exported_element=exp,
                exported_object='RawRaysOutgoing',
                dir_path=tmp_folder_path,
                sim_number='',
                rml_filename=os.path.join(tmp_folder_path, rml_filename)
            )
        log_message("Data Postprocessed")
    except IndexError as e:
        log_message(f"Data Postprocessed Failed: {e}")
        return False
    return True

def send_file_in_chunks(tmp_folder: str, result_filename: str, transport, chunk_size: int = 40960) -> None:
    """
    Sends a file in chunks over the network.

    Args:
        tmp_folder (str): Path to the temporary folder.
        result_filename (str): Name of the file to be sent.
        transport: The transport representing the connection.
        chunk_size (int, optional): Size of each chunk. Defaults to 40960.
    """
    result_path = os.path.join(tmp_folder, result_filename)
    
    with open(result_path, 'rb') as file:
        remaining_data = file.read()

        while remaining_data:
            chunk = remaining_data[:chunk_size]
            remaining_data = remaining_data[chunk_size:]

            while not chunk.endswith(b'\n') and remaining_data:
                next_byte = remaining_data[0:1]
                remaining_data = remaining_data[1:]
                chunk += next_byte

            transport.write(f"{result_filename}|||{chunk.decode('utf-8')}|||".encode('utf-8'))

def send_simulation_results(exports_list: List[str], tmp_folder: str, transport) -> None:
    """
    Sends simulation result files in chunks over the network.

    Args:
        exports_list (List[str]): List of objects to export during simulation.
        tmp_folder (str): Path to the temporary folder containing simulation results.
        transport: The transport representing the connection.
    """
    log_message("Start to send back the data")
    result_filename = 'beamline.rml'
    send_file_in_chunks(tmp_folder, result_filename, transport, chunk_size=40960)
    for obj in exports_list:
        result_filename = f'{obj}_analyzed_rays.dat'
        print(f'sending {result_filename}')
        send_file_in_chunks(tmp_folder, result_filename, transport, chunk_size=40960)
    transport.write(f"|ENDOFTRANSMISSION|".encode('utf-8'))
    log_message("Data sent")



class ServerProtocol(asyncio.Protocol):
    def __init__(self, tmp_folder):
        """
        Initializes the server protocol.

        Args:
            tmp_folder (str): Path to the temporary folder for storing received files.
        """
        self.tmp_folder = tmp_folder
        configure_logging(tmp_folder)
        log_message("Server started.")

    def connection_made(self, transport):
        """
        Called when a connection is made.

        Args:
            transport (asyncio.BaseTransport): The transport representing the connection.
        """
        peername = transport.get_extra_info('peername')
        log_message(f"Connection made from {peername}")
        print('\n\nConnection made:', peername)
        self.transport = transport

    def data_received(self, data):
        """
        Called when some data is received.

        This method is invoked when data is received over the network connection. It performs the following steps:

        1. Ensure the existence of the temporary folder for storing received files. If it doesn't exist, create it.

        2. Process the received data:
            - Decode the binary data into a UTF-8 string.
            - Split the string into two parts using '|||' as a separator, extracting the exports list and the file content.

        3. Save the received RML file content:
            - Construct the path to the RML file within the temporary folder.
            - Write the received file content to the RML file.

        4. Perform simulation and post-processing:
            - Split the exports list into individual items.
            - Call the `do_simulation` function to perform a simulation with the received exports list.
            - Call the `posptprocess_simulation` function to perform post-processing on the simulation results.

        5. Send simulation result files in chunks over the network:
            - Iterate through each object in the exports list.
            - Open each corresponding result file and send its content in chunks to the connected client.
            - Ensure each chunk ends with a complete row, and send the data using the established transport.

        6. Signal the end of data transmission:
            - Send "|ENDOFTRANSMISSION|" to indicate the completion of data transmission.

        Args:
            data (bytes): The received data.
        """
        create_temp_folder(self.tmp_folder)
        data_str = data.decode('utf-8')
        log_message("Data Received")

        exports_list, file_content = data_str.split('|||', 1)
        exports_list = exports_list.split(',')

        save_received_file(file_content, self.tmp_folder)
        simulation = perform_simulation(exports_list, self.tmp_folder)
        if not simulation:
            self.transport.write('SimulationError'.encode('utf-8'))
        
        postprocess = postprocess_simulation(exports_list, self.tmp_folder, 'beamline.rml')
        if postprocess:
            send_simulation_results(exports_list, self.tmp_folder, self.transport)
        else:
            self.transport.write('IndexError'.encode('utf-8'))

    def connection_lost(self, exc):
        """
        Called when the connection is lost.

        Args:
            exc (Exception): Exception indicating the reason for the connection loss.
        """
        if exc:
            log_message(f"Connection lost with exception: {exc}")
        else:
            log_message("Connection lost.")
        print("Connection lost:", exc)
