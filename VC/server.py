import asyncio
import websockets
import json

class WebSocketServer:
    def __init__(self, host="localhost", port=8888):
        self.host = host
        self.port = port
        self.server = None
        self.server_continue = None

    async def _handler(self, websocket, path):
        async for message in websocket:
            await self._handle_message(websocket, message)
    
    async def _handle_message(self, websocket, message):
        message = json.loads(message)
        print(message)
    
    async def send_message(self, websocket, message):
        await websocket.send(message)
    
    async def start(self):
        async with websockets.serve(self._handler, self.host, self.port):
            await asyncio.Future()

socket = WebSocketServer()
asyncio.run(socket.start())