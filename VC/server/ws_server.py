import asyncio
import websockets
import json
from serialInterface.serialInterface import SerialInterface
from instrumentation.labjackDriver import LabJackU6Driver
import logging

__name__ = "WebSocketServer"

class Command:
    def __init__(self, command, valve, action):
        self.command = command
        self.valve = valve
        self.action = action

class WebSocketServer:
    def __init__(self, host="192.168.0.1", port=8888):
        self.__host = host
        self.__port = port

        self.__logger = logging.getLogger(__name__)
        self.__log_handler = None

        self.__configure_log()

        self.__serial_interface = None
        self.__labjack = None

        try:
            self.__serial_interface = SerialInterface()
            self.__logger.info("Serial interface initialized\n")
        except Exception as e:
            self.__logger.error(f"Failed to initialize serial interface: {e}\n", exc_info=True)
            pass

        try:
            # self.__labjack = LabJackU6Driver()
            self.__logger.info("Labjack Driver initialized\n")
        except Exception as e:
            self.__logger.error(f"Failed to initailize labjack: {e}\n", exc_info=True)


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


    async def _handler(self, websocket):
        ''' 
        Name:
            WebSocketServer._handler(websocket=websockets.WebSocketServerProtocol, path= str) -> None
        Args:
            websocket: the websocket connection
        Desc:
            Handles the websocket connection
        '''
        while True:
            await self.__stream_reciever()
            await asyncio.sleep(0)
            async for message in websocket:
                await self._handle_message(websocket, message)


    async def __stream_reciever(self):
        message = self.__serial_interface.stream.readline().decode()
        print(message)
        self.__logger.info(f"Valve Cart Raw Feedback: {message}")


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
        async with websockets.serve(self._handler, self.__host, self.__port):
            await asyncio.Future()
