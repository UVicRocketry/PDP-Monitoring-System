import asyncio
import websockets
import json
from serialInterface import SerialInterface
from labjackDriver import LabJackU6Driver

class Command:
    def __init__(self, command, valve, action):
        self.command = command
        self.valve = valve
        self.action = action

class WebSocketServer:
    def __init__(self, host="localhost", port=8888):
        self.__host = host
        self.__port = port
        self.server = None
        self.server_continue = None
        try:
            self._serial_interface = SerialInterface()
        except:
            pass
        try:
            self.labjack = LabJackU6Driver()
        except:
            pass
    async def _handler(self, websocket):
        ''' 
        Name:
            WebSocketServer._handler(websocket=websockets.WebSocketServerProtocol, path= str) -> None
        Args:
            websocket: the websocket connection
        Desc:
            Handles the websocket connection
        '''
        async for message in websocket:
            await self._handle_message(websocket, message)
    
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

                command_message = self._serial_interface.build_message(
                    command.command, 
                    command.valve, 
                    command.action)

                self._serial_interface.send(command_message)
                await websocket.send(json.dumps({'identifier': 'CONTROLS', 'data': 'Controls received'}))

            case 'INFO':

                pass
            case 'INSTRUMENTATION':
                pass
            case _:
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

socket = WebSocketServer()
asyncio.run(socket.start())