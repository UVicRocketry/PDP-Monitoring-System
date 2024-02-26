import asyncio
import websockets

class WebSocketServer:
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.server = None
        self.server_continue = None
        self.loop = asyncio.get_event_loop()

    async def _handler(self, websocket, path):
        async for message in websocket:
            await self._handle_message(websocket, message)
    
    async def _handle_message(self, websocket, message):
        message = message.strip()
        match message.identifier:
            case "instrumentation":
                await self.send_message(websocket, "Received instrumentation message")
            case "controls":
                await self.send_message(websocket, "Received controls message")
    
    async def send_message(self, websocket, message):
        await websocket.send(message)
    
    def start(self):
        self.server = websockets.serve(self.handler, self.host, self.port)
        asyncio.get_event_loop().run_until_complete(self.server)
        asyncio.get_event_loop().run_forever()

    async def stop(self):
        self.server.close()
        self.loop.run_until_complete(self.server.wait_closed())
