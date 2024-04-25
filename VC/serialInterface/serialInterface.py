# reference https://github.com/UVicRocketry/Hybrid-Controls-System/blob/33-comms-prot-fixing/src/MCC_GUI/comm.py
import serial
import logging
from enum import Enum
from .serialCommandTypes import Valves, DataTypes, DataLabels, DataValues, SOURCE_TAG
import platform
import asyncio
import json


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
        __process_command: processes a command
    """
    def __init__(self):

        self.__logger = logging.getLogger(__name__)
        self.__log_handler = None
        self.__configure_log()

        # lists all possible com ports
        self.__port = None 
        self.stream = None
        self.__init_stream()

        self._connected = False

        self.__valve_state = {
            Valves.MEV: DataValues.CLOSED,
            Valves.N2OF: DataValues.CLOSED,
            Valves.N2OV: DataValues.CLOSED,
            Valves.N2F: DataValues.CLOSED,
            Valves.RTV: DataValues.CLOSED,
            Valves.NCV: DataValues.CLOSED,
            Valves.ERV: DataValues.CLOSED,  
        }


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
            SerialInterface._initstream() -> None
        Desc:
            Initializes the serial port and sets the connection status
        '''
        try:
            print("OS: ", OS)
            self.__port = 'COM6' if str(OS) == 'Windows' else '/dev/ttyACM0' # update this to the correct port for the VC mini PC
            self.stream = serial.Serial(port=self.__port, baudrate=115200, timeout=0.1)
            self.__logger.info(f"Opened serial port: {self.__port}")
        except Exception as e:
            self.__logger.error(f"failed to open serial: {e}")
            raise e


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
            if self.stream.in_waiting > 0:
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
            self.stream.close()
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
        with self.__message_queue.mutex:
            self.__message_queue.queue.clear()
        self.__send("MCC,ABORT,")


    def __send(self, message) -> bool:
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
            self.stream.write(message.encode())
            return True
        except:
            return False
     

    def receive(self) -> str:
        '''
        Name: 
            SerialInterface._receive() -> bool
        Desc: 
            Receives a message from the serial port. Should only be called on a 
            threaded process otherwise the program will hang.
        Returns:
            True if the message was received successfully, False otherwise
        '''
        message = self.stream.readline().decode()
        self.__logger.info(f"VC Raw message received: {message}")
        # if "\n'" in feedback:
        #     print("contains /\n/")
    
        return message
    
    async def receive_loop(self, queue: asyncio.LifoQueue):
        '''
        Name:
            SerialInterface.receive_loop() -> None
        Desc:
            The main loop for receiving messages
        '''
        while True:
            if self.message_pending:
                message = self.receive()
                print(f"[Serial] Received message: {message}")
                await queue.put(message)
                # if message:
                #     self.__process_command(message)
            await asyncio.sleep(0.1)

    async def send_async(self, queue: asyncio.LifoQueue):
        '''
        Name:
            SerialInterface.send_async() -> None
        Desc:
            The main loop for sending messages
        '''
        while True:
            if not queue.empty():
                message = await queue.get()
                print(f"\n[Serial] Sending message: {message}\n")
                message_object = json.loads(message)
                if "command" in message_object: 
                    command = self.build_valve_message(
                        message_object['command'], 
                        message_object['valve'], 
                        message_object['action'])
                    self.__send(command)
            await asyncio.sleep(0.1)


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


    def __process_incoming_command(self, message):
        '''
        Name:
            SerialInterface.__process_command(message= str) -> None
        Args:
            message: the message to process
        Desc:
            Processes a message from the MCC
        '''
        is_message_processed = False
        if message.endswith('\n'):
            message_array = message.strip().split(',')
            match message_array[1]:
                case ResponseCommandType.SWITCH_STATE:
                    try:
                        self.__logger.info(f"SET SWITCH STATE: {message_array[2]}, {message_array[2]}")
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
                    for i in range(2, len(message_array)):
                        valve = message_array[i]
                        action = message_array[i + 1]
                        if self.__valve_state[valve] != action:
                            self.__valve_state[valve] = action
                            command = {
                                'identifier': 'CONTROLS',
                                'command': 'FEEDBACK',
                                'valve': valve,
                                'action': action   
                            }
                            print(command)
                            self.__logger.info(f"=Feedback: {valve} is {action}")
                        is_message_processed = True

