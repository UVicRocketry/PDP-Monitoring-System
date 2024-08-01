from server.ws_server import WebSocketServer
from instrumentation.labjackDriver import LabJackU6Driver
import asyncio

INSTRUMENTATION_PORT = 8888

def main() -> None:
    '''
    Name:
        main() -> None
    Desc:
        Main entry point for the valve cart. There are two websocket servers required, one for serail and one for instrumentation. 
        Without two servers the one connection will be overloaded by traffic close abruptly.
    '''
    instrumentation = None
    wss_instrumentation = None
    
    # the queues are used to send commands and feecback from task to task. 
    # ex: wss (command) -> serail(move valve); serail (feedback) -> wss (feedback) 
    instrumentation_feedback_queue = asyncio.LifoQueue()

    try:
        instrumentation = LabJackU6Driver(test_mode=True)
        print("instrumentation Driver configured")
    except Exception as e:
        print(f"Failed to initialize LabJackU6Driver: {e}")
        exit(1)

    try:
        wss_instrumentation = WebSocketServer(port=INSTRUMENTATION_PORT)
    except Exception as e:
        print(f"Failed to initialize websocket server: {e}")
        exit(1)

    event_loop = asyncio.get_event_loop() 

    # Websocket server for instrumentation
    event_loop.create_task(wss_instrumentation.start())

    # Instrumentation
    event_loop.create_task(instrumentation.mock_stream(instrumentation_feedback_queue))
    
    # websockets handler
    event_loop.create_task(wss_instrumentation.instrumentation_wss_handler(instrumentation_feedback_queue))

    
    try:
        event_loop.run_forever()
    except KeyboardInterrupt:
        event_loop.close()
        print("program terminated by user")
        exit(0)

if __name__ == "__main__":
    main()
