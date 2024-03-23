# reference https://github.com/UVicRocketry/Hybrid-Controls-System/blob/33-comms-prot-fixing/src/MCC_GUI/comm.py

import serial 
import queue
import logbook
import os
import sys
from serialCommandTypes import Valves, DataTypes, DataLabels, DataValues, SOURCE_TAG

class SerialInterface:
    def __init__(self):
        self._message_queue = queue.Queue()
        self._control_queue = queue.Queue()
        self._verbose=False
        self._logger = logbook.Logger("SerialInterface")
        self.__log = None
        self._port = "COM6" #set blank port if no config file
        self._connected = False
        self._desyncList=[]
        self._status="DCONN"
        self.valves= [
            Valves.N2OF,
            Valves.N2OV,
            Valves.N2F,
            Valves.RTV,
            Valves.NCV,
            Valves.EVV,
            Valves.IGPRIME,
            Valves.IGFIRE,
            Valves.MEV
        ]
        self.__configure_log()
        self.__init_stream()
    
    def __configure_log(self):
        '''
        Name:
            SerialInterface.configureLog() -> None
        Desc:
            Configures the log file
        '''
        self.__log = logbook.FileHandler('serial.log', level='DEBUG', bubble=True)
        self.__log.format_string = '{record.time:%Y-%m-%d %H:%M:%S.%f%z} [{record.level_name}] {record.channel}: {record.message}'
        self.__log.push_application()

    def __init_stream(self):
        '''
        Name:
            SerialInterface._init_stream() -> None
        Desc:
            Initializes the serial port and sets the connection status
        '''
        try:
            self._stream = serial.Serial(port="COM6", baudrate=115200, timeout=0.1)
        except serial.SerialException as e:
            print(f"failed to open serial: {e}")
            pass
    

    def init_connection(self):
        '''
        Name:
            SerialInterface.init_connection() -> None
        Desc:
            Initializes the connection to the Mission Control
        '''
        while True:
            self._send("MCC,CONNECT,")
            with self.message_queue.mutex:
                self.message_queue.queue.clear()

            try:
                config_message = self.message_queue.get(timeout=3)
                if ",STATUS,ESTABLISH" in config_message:
                    self._connected = True
                    self._status = "CONN"
                    break 
            except queue.Empty:
                self._status = "ERR"
                break
    
    @property
    def message_pending(self) -> bool:
        '''
        Name:
            SerialInterface.message_pending() -> bool
        Desc:
            Checks if theres any bytes in the serial buffer
        Returns:
            True if there is a message pending, False otherwise
        '''
        try:
            if self._stream.in_waiting > 0:
                return True
            else:
                return False
        except:
            return False
    

    def close(self) -> bool:
        '''
        Name:
            SerialInterface.close() -> None
        Desc:
            Closes the serial port
        Returns:
            True if the port was closed successfully, False otherwise
        '''
        try: 
            self._stream.close()
            self._connected = False
            return True
        except:
            return False


    def _abort(self):
        '''
        Name:
            SerialInterface._abort() -> None
        Desc:
            Sends an abort signal to the MCC
        '''

        with self.message_queue.mutex:
            self.message_queue.queue.clear()
        self._send("MCC,ABORT,")


    def send(self, message) -> bool:
        '''
        Name: 
            SerialInterface._send(message= str) -> bool
        Args:
            message: the message to send
            Returns:
            True if the message was sent successfully, False otherwise

        Desc: Sends a message to the serial port
        '''
        try: 
            self._stream.write(message.encode())
            if self._verbose:
                pass
            return True
        except:
            return False
        
    
    def _receive(self) -> bool:
        '''
        Name: 
            SerialInterface._receive() -> bool
        Desc: 
            Receives a message from the serial port. Should only be called on a 
            threaded process otherwise the program will hang.
        Returns:
            True if the message was received successfully, False otherwise
        '''
        message = ""
        try:
            message = message + self._stream.readline().decode()
            if message.endswith("\n"):
                message = message.strip()
                self.message_queue.put(message)
            else: 
                self._log.log("WARN", f"Received incomplete message: {message}")

            if "ABORT" in message:
                with self.message_queue.mutex:
                        self.message_queue.queue.clear()
                self.message_queue.put(message)

        except:
            self._log.log("WARN", f"Failed to receive: {message}")
            return False
        
        return True
    
    def build_message(self, data_type, data_label, data_value, source_tag=SOURCE_TAG) -> str:
        '''
        Name:
            SerialInterface.build_message(source_tag="VC", data_type= DataTypes, data_label= DataLabels, data_value= DataValues) -> str
        Args:
            source_tag: the source of the command
            data_type: the type of data
            data_label: the label of the data
            data_value: the value of the data
        Returns:
            A string representing the command
        Desc:
            Builds a command string
        '''
        # example message f"VC,CTRL,MEV,OPEN\n"
        return f"VC,{data_type},{data_label},{data_value}\n"

    def process_command(self, message):
        '''
        Name:
            SerialInterface.process_command(message= str) -> None
        Args:
            message: the message to process
        Desc:
            Processes a message from the MCC
        '''
        if "," in message:
            current_message = message.split(",")
            match current_message[0]:
                case DataTypes.SUMMARY:
                    self._process_summary_command(current_message)
                case _:
                    self._log.log("ERROR", f"Invalid message: {message}")

    def _process_summary_command(self, message):
        '''
        Name:
            SerialInterface._process_summary_command(message= str) -> None
        Args:
            message: the message to process
        Desc:
            Processes a summary command from the Mission Control
        '''
        if self._verbose:
            self._log.log("INFO", f"Received summary command: {message}")
        for i in range(2, len(message), 2):
            self._conf[message[i]] = message[i + 1]
            if self._verbose:
                self._log.log(f"INFO {message[i]} {message[i + 1]}")