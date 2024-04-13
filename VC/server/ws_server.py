import asyncio
import websockets
import json
from serialInterface.serialInterface import SerialInterface
from instrumentation.labjackDriver import LabJackU6Driver
import logging
import platform

__name__ = "WebSocketServer"

OS = platform.system()

HOST = "192.168.0.1" if OS == "Linux" else "localhost"
PORT = 8888

class Command:
    def __init__(self, command, valve, action):
        self.command = command
        self.valve = valve
        self.action = action

class WebSocketServer:
    def __init__(self, host=HOST, port=PORT):
        self.__host = host
        self.__port = port

        self.__logger = logging.getLogger(__name__)
        self.__log_handler = None

        self.__configure_log()

        self.__serial_interface = None
        self.__labjack = None

        self.__feedback_reception_task = None
        self.__labjack_task = None
        self.__ws_reception_task = None
        self.__coroutines_configured = False
        self.__comm_manager_event_loop = asyncio.get_event_loop()

        try:
            self.__serial_interface = SerialInterface()
            self.__logger.info("Serial interface initialized\n")
        except Exception as e:
            self.__logger.error(f"Failed to initialize serial interface: {e}\n", exc_info=True)
            pass

        try:
            # self.__labjack = LabJackU6Driver()
            # self.__labjack_task = asyncio.create_task(self.__labjack.start())
            self.__logger.info("Labjack Driver initialized\n")
        except Exception as e:
            self.__logger.error(f"Failed to initailize labjack: {e}\n", exc_info=True)


    def __setup_coroutines(self, websocket):
        '''
        Name:
            WebSocketServer.__setup_coroutines(websocket= websockets.WebSocketServerProtocol) -> None
        Args:
            websocket: the websocket connection
        Desc:
            Sets up the coroutines for the websocket
        '''
        try:
            self.__feedback_reception_task = asyncio.create_task(self.__stream_receiver(websocket))
            self.__logger.info("Serial coroutine initialized\n")
            self.__ws_reception_task = asyncio.create_task(self.__ws_receiving_handler(websocket))
            self.__logger.info("WS coroutine initialized\n")
            self.__coroutines_configured = True
        except Exception as e:
            self.__logger.error(f"Failed to coroutines: {e}\n", exc_info=True)


    def __configure_log(self):
        '''
        Name:
            WebSocketServer.__configure_log() -> None
        Desc:
            Configures the log file
        '''
        self.__log_handler = logging.FileHandler('ws-server.log', mode='w')
        formatter = logging.Formatter('[%(name)s] %(asctime)s [%(levelname)s]: %(message)s')
        self.__log_handler.setFormatter(formatter)
        self.__logger.addHandler(self.__log_handler)
        self.__logger.setLevel(logging.INFO)
        self.__logger.info("WS Logger configured\n")


    async def __handler(self, websocket):
        ''' 
        Name:
            WebSocketServer.__handler(websocket=websockets.WebSocketServerProtocol, path= str) -> None
        Args:
            websocket: the websocket connection
        Desc:
            Handles the websocket requests and serial receiving
        '''

        if not self.__coroutines_configured: 
            self.__setup_coroutines(websocket)
        
        await self.__start_coroutines()
        await asyncio.sleep(0)
        # finally:
        #     self.__event_loop.close()

    
    async def __start_coroutines(self):
        await asyncio.gather(self.__ws_reception_task, self.__feedback_reception_task)


    async def __ws_receiving_handler(self, websocket):
        '''
        Name:
            WebSocketServer.__ws_recieving_handler(websocket=websockets.WebSocketServerProtocol) -> None
        Args:
            websocket: the websocket connection
        Desc:
            Handles the 
        '''
        async for message in websocket:
            await self._handle_message(websocket, message)
            await asyncio.sleep(0)


    async def __stream_receiver(self, websocket):
        if self.__serial_interface is None:
            return

        message = self.__serial_interface.receive()
        self.__logger.info(f"Valve Cart Raw Feedback: {message}")
        await asyncio.sleep(0)
        # if self.__serial_interface.message_pending:


    async def __feedback_builder(self, message):
        '''
        Name:
            WebSocketServer.__feedback_builder(message= str) -> str
        Args:
            message: the message to build
        Desc:
            Builds the feedback message
        '''
        return json.dumps({'identifier': 'FEEDBACK', 'data': message})


    async def _handle_message(self, websocket, message):
        '''
        Name:
            WebSocketServer._handle_message(websocket=websockets.WebSocketServerProtocol, message= str) -> None
        Args:
            websocket: the websocket connection
            message: the message to handle
        Desc:
            Handles a message from the websocket
        '''
        message = json.loads(message)
        print(message)
        message_identifier = message['identifier'] if 'identifier' in message else None
        
        match message_identifier:
            case 'CONTROLS':
                command = Command(
                    message['command'], 
                    message['valve'], 
                    message['action'])

                command_message = self.__serial_interface.build_valve_message(
                    command.command, 
                    command.valve, 
                    command.action)
                
                self.__logger.info(f"SENDING COMMAND: {command_message}\n")

                self.__serial_interface.send(command_message)
                try: 
                    await websocket.send(json.dumps({'identifier': 'CONTROLS', 'data': 'Controls received'}))
                except Exception as e:
                    self.__logger.error(f"Failed to send message: {e}", exc_info=True)

            case 'CONFIGURATION':
                pass
            case 'INSTRUMENTATION':
                pass
            case _:
                self.__logger.error(f"INVALID COMMAND: {message}", exc_info=True)
                pass

    
    async def send_message(self, websocket, message):
        '''
        Name:
            WebSocketServer.send_message(websocket= websockets.WebSocketServerProtocol, message= str) -> None
        Args:
            websocket: the websocket connection
            message: the message to send
        Desc:
            Sends a message to the mission control
        '''
        await websocket.send(message)


    async def start(self):
        '''
        Name:
            WebSocketServer.start() -> None
        Desc:
            Starts the websocket server
        '''
    
        async with websockets.serve(self.__handler, self.__host, self.__port):
            await asyncio.Future()
        
