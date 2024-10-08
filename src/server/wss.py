import asyncio
import websockets
import json
import logging
import platform

__name__ = "WebSocketServer"

OS = platform.system()

HOST = "192.168.0.1" if OS == "Linux" else "localhost"
PORT_SERIAL = 8080
PORT_INSTRUMENTATION = 8888

INSTRUMENTATION_FILE_DATA_PATH = 'tmp.txt'

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
    def __init__(self, ws_type: str):
        self.__ws_type = ws_type
        if self.__ws_type == "instrumentation":
            self.__port = PORT_INSTRUMENTATION
        else:
            self.__port = PORT_SERIAL

        print(f'type:{self.__ws_type}, port:{self.__port}')

        self.__host = HOST
        
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
            with open('instrumentation/tmp.txt', 'r') as file:
                lines = file.readlines()
                if len(lines) > 1:
                    await websocket.send(json.dumps({
                        "identifier": "INSTRUMENTATION",
                        "data": json.loads(lines[0])
                    })) 
                    await asyncio.sleep(0.1)


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
        async with websockets.serve(self.__serial_handler, self.__host, self.__port):
            await asyncio.Future()

    async def start_instrumentation(self):
        '''
        Name:
            WebSocketServer.start() -> None
        Desc:
            Starts the websocket server
        '''
        async with websockets.serve(self.__instrumentation_handler, self.__host, self.__port):
            await asyncio.Future()
        