from server.ws_server import WebSocketServer
from serialInterface.serialInterface import SerialInterface
import asyncio

def main() -> None:
    '''
    Name:
        main() -> None
    Desc:
        Main entry point for the VC program
    '''
    serial = None
    wss = None
    
    serial_feedback_queue = asyncio.LifoQueue()
    serial_command_queue = asyncio.LifoQueue()

    try:
        serial = SerialInterface(serial_command_queue, serial_feedback_queue)
    except Exception as e:
        print(f"Failed to initialize serial interface: {e}")
        exit(1)

    try:
        wss = WebSocketServer(serial_command_queue, serial_feedback_queue)
    except Exception as e:
        print(f"Failed to initialize websocket server: {e}")
        exit(1)
       

    event_loop = asyncio.get_event_loop() 

    # Serial sending and receiving tasks
    event_loop.create_task(serial.receive_loop(serial_feedback_queue))
    event_loop.create_task(serial.send_async(serial_command_queue))

    # WebSocket server task
    event_loop.create_task(wss.start())
    
    try:
        event_loop.run_forever()
    except KeyboardInterrupt:
        event_loop.close()
        print("VC program terminated by user")
        exit(0)

if __name__ == "__main__":
    main()
