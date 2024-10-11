import asyncio
from wss import WebSocketServer

__name__ = "LJWebsocket"

if __name__ == "__main__" or __name__ == "LJWebsocket":
    print("Entered Instrumentation")
    ws = WebSocketServer("instrumentation")
    asyncio.run(ws.start_instrumentation())
