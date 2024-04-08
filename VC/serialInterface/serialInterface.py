# reference https://github.com/UVicRocketry/Hybrid-Controls-System/blob/33-comms-prot-fixing/src/MCC_GUI/comm.py
import serial
import queue
import logging
from enum import Enum
from .serialCommandTypes import Valves, DataTypes, DataLabels, DataValues, SOURCE_TAG
import platform

__name__ = "SerialInterface"

OS = platform.system()

class ResponseCommandType(Enum):
    SUMMARY = "SUMMARY"
    START_UP = "STARTUP"
    STATUS = "STATUS"
    SWITCH_STATE = "SWITCHSTATE"
    DISARMED = "DISARMED"
    ARMED = "ARMED"
    ABORTED = "ABORTED"
    ERROR = "ERROR"
    UNKNOWN_COMMAND = "UNKNOWNCOMMAND"

class SerialInterface:
    """
    Name:
        SerialInterface
    Desc:
        The serial interface for the VC to communicate with the controls arduino

    Attributes:

    Public:
        message_queue: the queue for messages
        control_queue: the queue for control messages
        verbose: the verbosity of the interface
        connected: the connection status
        status: the status of the connection
        valves: the list of valves
    
    Public Methods:
        init_connection: initializes the connection
        message_pending: checks if there is a message pending
        close: closes the serial port
        send: sends a message
        build_valve_message: builds a message
        process_command: processes a command
        _process_summary_command: processes a summary command

    """
    def __init__(self):
        self._message_queue = queue.Queue()
        self._control_queue = queue.Queue()
        self._verbose=False

        self.__logger = logging.getLogger(__name__)
        self.__log_handler = None
        self.__configure_log()

        # lists all possible com ports
        self.__possible_ports = None
        self.__port = None 
        self._stream = None
        self.__init_stream()

        self._connected = False
        self._status="DCONN"

        self.valves = [
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


    def __configure_log(self):
        '''
        Name:
            SerialInterface.configureLog() -> None
        Desc:
            Configures the log file
        '''
        self.__log_handler = logging.FileHandler('serial.log', mode='w')
        formatter = logging.Formatter('[%(name)s] %(asctime)s [%(levelname)s]: %(message)s')
        self.__log_handler.setFormatter(formatter)
        self.__logger.addHandler(self.__log_handler)
        self.__logger.setLevel(logging.INFO)
        self.__logger.info("Serial Logger configured")


    def __init_stream(self):
        '''
        Name:
            SerialInterface._init_stream() -> None
        Desc:
            Initializes the serial port and sets the connection status
        '''
        try:
            print("OS: ", OS)
            self.__port = 'COM6' if str(OS) == 'Windows' else '/dev/ttyACM0' # update this to the correct port for the VC mini PC
            self._stream = serial.Serial(port=self.__port, baudrate=115200, timeout=0.1)
            self.__logger.info(f"Opened serial port: {self.__port}")
        except Exception as e:
            self.__logger.error(f"failed to open serial: {e}")
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
                self.__logger.info(f"Received incomplete message: {message}")

            if "ABORT" in message:
                with self.message_queue.mutex:
                        self.message_queue.queue.clear()
                self.message_queue.put(message)

        except:
            self.__logger.info(f"Failed to receive: {message}")
            return False
        
        return True


    def build_valve_message(self, data_type, data_label, data_value, source_tag=SOURCE_TAG) -> str:
        '''
        Name:
            SerialInterface.build_valve_message(source_tag="VC", data_type= DataTypes, data_label= DataLabels, data_value= DataValues) -> str
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
        is_message_processed = False
        if message in ',':
            message_array = message.split(',')
            match message_array[1]:
                case ResponseCommandType.SWITCH_STATE:
                    try:
                        self.___logger.info(f"SET SWITCH STATE: {message_array[2]}, {message_array[2]}")
                        # send to 
                        is_message_processed = True
                    except:
                        is_message_processed = False
                    return is_message_processed
                
                case ResponseCommandType.STATUS:

                    if message_array[2] == ResponseCommandType.START_UP:
                        pass
                    
                    elif message_array[2] == ResponseCommandType.DISARMED:
                        pass

                    elif message_array[2] == ResponseCommandType.ARMED:
                        pass

                    elif message_array[2] == ResponseCommandType.ABORTED:
                        pass

                    elif message_array[2] == ResponseCommandType.ERROR:
                        pass

                    else:
                        self.___logger.error(f"UNKNOWN STATUS: {message_array[2]}")
            
                case ResponseCommandType.SUMMARY:
                    try:
                        self.___logger.info(f"SUMMARY: {message_array[2]}")
                        is_message_processed = True
                    except:
                        is_message_processed = False
                    return is_message_processed


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
            self.__logger.info("INFO", f"Received summary command: {message}")
        for i in range(2, len(message), 2):
            self._conf[message[i]] = message[i + 1]
            if self._verbose:
                self.__logger.info(f"INFO {message[i]} {message[i + 1]}")
