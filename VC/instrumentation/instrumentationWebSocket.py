import websockets
import asyncio
import platform
import json
OS = platform.system()

# Constants
INSTRUMENTATION_FILE_PATH = "instrumentation-data.txt"
INSTRUMENATATION_PORT = "8888"
HOST = "192.168.0.1" if OS == "Linux" else "localhost"

async def handler(websocket):
    with open("instrumentation-data.txt", 'r') as file:
        print("handler")
        while True: 
            data = file.readline()
            print(data)
            await websocket.send(json.dumps({
                "identifier": "INSTRUMENTATION",
                "data": json.loads(data)
            }))
            await asyncio.sleep(1)

async def start():
    async with websockets.serve(handler, "192.168.0.1", '8888'):
        await asyncio.Future()

asyncio.run(start())

