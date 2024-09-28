import asyncio
from ..server.ws_server import WebSocketServer

__name__ = "LJWebsocket"

if __name__ == "__main__" or __name__ == "LJWebsocket":
    ws = WebSocketServer("instrumentation")
    asyncio.run(ws.start_instrumentation())
