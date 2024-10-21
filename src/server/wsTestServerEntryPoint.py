import asyncio
from wss import WebSocketServer

__name__ = "TestServer"

def main() -> None:
    serial_wss = None
    instrumentation_wss = None

    try: 
        serial_wss = WebSocketServer(ws_type="SERIAL_WS", test_mode=True)
        instrumentation_wss = WebSocketServer(ws_type="INSTRUMENTATION_WS", test_mode=True)
    except Exception as e:
        print(f"Failed to initialize websocket server: {e}")
        exit(1)

    event_loop = asyncio.get_event_loop()
    try:
        event_loop.create_task(serial_wss.start_serial())
        event_loop.create_task(instrumentation_wss.start_instrumentation())
    except Exception as e:
        print(f"Failed to start websocket server: {e}")
        exit(1)

    try:
        event_loop.run_forever()
    except KeyboardInterrupt:
        event_loop.close()
        print("Test Server terminated by user")
        exit(0)

if __name__ == "TestServer" or __name__ == "__main__":
    main()
