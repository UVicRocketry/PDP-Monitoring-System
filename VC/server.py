import socket 
import threading

# local host
HOST = '127.0.0.1'
PORT = 9001 

def handle_client(client_socket):
    while True:
        data = client_socket.recv(1024)
        if not data:
            break

        print()
        client_socket.sendall(data)
    client_socket.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:

    server.bind((HOST, PORT))
    server.listen()

    while True:
        connection, address = server.accept()
        
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()
