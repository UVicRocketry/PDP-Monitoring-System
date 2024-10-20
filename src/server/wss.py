import os 
import asyncio
import time
import websockets
import json
import logging
import platform
# from .instrumentationMock import labjack_mock as lj_mock
# from .serailMock import serial_feedback_mock as serial_mock

__name__ = "WebSocketServer"

OS = platform.system()

HOST_PRODUCTION = "192.168.0.1" 
HOST_TEST = "localhost"

PORT_SERIAL = 8080
PORT_INSTRUMENTATION = 8888

INSTRUMENTATION_FILE_DATA_PATH = '/home/uvr/Documents/GitHub/PDP-Monitoring-System/src/instrumentation/tmp.txt'

INSTRUMENTATION_WS_TYPE = "INSTRUMENTATION_WS"
SERIAL_WS_TYPE = "SERIAL_WS"

class Command:
    def __init__(self, command, valve, action):
        self.command = command
        self.valve = valve
        self.action = action

class VCFeedback:
    def __init__(self, valve, action):
        self.identifier = "FEEDBACK",
        self.valve = valve,
        self.action = action

class WebSocketServer:
    def __init__(self, ws_type: str, test_mode: bool = False):
        self.__ws_type = ws_type
        self.__test_mode = test_mode
        self.__host = HOST_PRODUCTION

        if test_mode:
            self.__test_mode = True
            self.__host = HOST_TEST

        if self.__ws_type == INSTRUMENTATION_WS_TYPE:
            self.__port = PORT_INSTRUMENTATION
        else:
            self.__port = PORT_SERIAL

        print(f'type:{self.__ws_type}, port:{self.__port}, host:{self.__host}')
        
        self.__wss_instance = None

        self.__logger = logging.getLogger(__name__)
        self.__log_handler = None

        self.__incoming_queue = asyncio.LifoQueue()
        self.__configure_log()


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


    async def __serial_handler(self, websocket):
        ''' 
        Name:
            WebSocketServer.__handler(websocket=websockets.WebSocketServerProtocol, path= str) -> None
        Args:
            websocket: the websocket connection
        Desc:
            Handles the websocket requests and serial feedback to send over the websocket
        '''
        self.__wss_instance = websocket
        await self.__wss_instance.send(json.dumps({
            "identifier": "STARTUP", 
            "data": "VC CONNECTED"
        }))
        self.__logger.info(f"VC Connected")
        async for message in websocket:
            await self.__incoming_queue.put(message)
            self.__incoming_queue.task_done()
            await asyncio.sleep(0)
    
    
    async def __instrumentation_handler(self, websocket):
        '''
        ame:
            WebSocketServer.__handler(websocket=websockets.WebSocketServerProtocol, path= str) -> None
        Args:
            websocket: the websocket connection
        Desc:
            Handles the websocket requests and serial feedback to send over the websocket
        '''
        print("instrumentation handler")
        while True:
            with open(INSTRUMENTATION_FILE_DATA_PATH, 'r') as file:
                lines = file.readlines()
                if len(lines) > 1:
                    await websocket.send(json.dumps({
                        "identifier": "INSTRUMENTATION",
                        "data": json.loads(lines[0])
                    })) 
                    await asyncio.sleep(0.001)


    async def __test_instrumentation__handler(self, websocket):
        print("Test Instrumentation Handler")
        while True:
            packet = lj_mock()
            await websocket.send(json.dumps({
                "identifier": "INSTRUMENTATION",
                "data": packet
            }))
            await asyncio.sleep(0)


    async def __test_serial_handler(self, websocket):
        print("Test Serial Handler")
        while True:
            async for message in websocket:
                packet = json.loads(message)
                await websocket.send(json.dumps(serial_mock(valve=packet['valve'], action='TRANSIT')))
                print(f"Sent: {packet['valve']} TRANSIT")
                time.sleep(3)
                feedback = serial_mock(valve=packet['valve'], action=packet['action'])
                print(f"Sent: {feedback}")
                await websocket.send(json.dumps(feedback))
            await asyncio.sleep(0)


    async def wss_reception_handler(self, queue):
        while True:
            message = await self.__incoming_queue.get()
            await queue.put(message)
            await asyncio.sleep(0)

    
    async def serial_feedback_wss_handler(self, queue):
        '''
        Name:
            WebSocketServer.__serial_feedback_wss_handler(websocket= websockets.WebSocketServerProtocol) -> None
        Args:
            websocket: the websocket connection
        Desc:
            Handles the serial feedback from the self.serial_queue to send over the websocket
        '''
        while True:
            feedback = None
            if self.__wss_instance is not None:
                try:
                    # Try to get feedback from the serial queue. if none available then continue to the next iteration
                    feedback = await queue.get() 
                    self.__logger.info(f"Received from serial feedback: {feedback}")
            
                    await self.__wss_instance.send(json.dumps({
                        "identifier": "FEEDBACK",
                        "data": feedback
                    }))

                except asyncio.QueueEmpty:
                    await asyncio.sleep(0)
                    return
                
            await asyncio.sleep(0)

    
    async def send_message(self, message):
        '''
        Name:
            WebSocketServer.send_message(websocket= websockets.WebSocketServerProtocol, message= str) -> None
        Args:
            websocket: the websocket connection
            message: the message to send
        Desc:
            Sends a message to the mission control
        '''
        await self.__wss_instance.send(message)


    async def start_serial(self):
        '''
        Name:
            WebSocketServer.start() -> None
        Desc:
            Starts the websocket server
        '''
        handler = self.__serial_handler if not self.__test_mode else self.__test_serial_handler
        async with websockets.serve(handler, self.__host, self.__port):
            await asyncio.Future()

    async def start_instrumentation(self):
        '''
        Name:
            WebSocketServer.start() -> None
        Desc:
            Starts the websocket server
        '''
        handler = self.__instrumentation_handler if not self.__test_mode else self.__test_instrumentation__handler
        async with websockets.serve(handler, self.__host, self.__port):
            await asyncio.Future()
