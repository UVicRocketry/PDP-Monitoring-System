from server.ws_server import WebSocketServer
import asyncio

def main() -> None:
    '''
    Name:
        main() -> None
    Desc:
        Main entry point for the VC program
    '''
    socket = WebSocketServer()
    asyncio.run(socket.start())

if __name__ == "__main__":
    main()