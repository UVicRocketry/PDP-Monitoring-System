import json
import random
import time
import tornado.ioloop
import tornado.web
import tornado.websocket

clients = set()  # Keep track of connected clients

# Function to generate a dictionary with fixed keys and random values
def generate_data():
    return {
        "P_INJECTOR": random.randint(0, 1000000),
        "P_COMB_CHMBR": random.randint(0, 500000),
        "P_N2O_FLOW": random.randint(0, 1000000),
        "P_N2_FLOW": random.randint(0, 1000000),
        "P_RUN_TANK": random.randint(0, 1000000),

        "T_RUN_TANK": random.randint(200, 300),
        "T_INJECTOR": random.randint(200, 300),
        "T_COMB_CHMBR": random.randint(300, 1500),
        "T_POST_COMB": random.randint(300, 1500),

        "L_RUN_TANK": random.randint(0, 20),
        "L_THRUST": random.randint(0, 1200)
    }

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        clients.add(self)
        print("New client connected.")

    def on_close(self):
        clients.remove(self)
        print("Client disconnected.")

# Function to send data to clients
def send_data():
    data = generate_data()
    json_data = json.dumps({'data':data})
    for client in clients:
        client.write_message(json_data)  # Send to each connected client
    #print("Sent data:", json_data)
    tornado.ioloop.IOLoop.current().call_later(0.001, send_data)  # Call again in 1 second

def make_app():
    return tornado.web.Application([
        (r'/websocket', WebSocketHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)  # Choose an appropriate port
    print("Starting WebSocket server on port 8888...")
    send_data()  # Start sending data
    tornado.ioloop.IOLoop.current().start()  # Start the Tornado I/O loop

