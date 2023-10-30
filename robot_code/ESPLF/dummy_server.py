import socket
import json

# Define the server address and port
HOST = '127.0.0.1'  # Loopback address
PORT = 12345  # You can choose any available port

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the server address and port
server_socket.bind((HOST, PORT))

# Listen for incoming connections
server_socket.listen(1)  # Allow one connection at a time

print(f"Server listening on {HOST}:{PORT}")

while True:
    # Accept a connection from a client
    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address}")

    try:
        # Define a sample JSON data
        json_data = {
            'message': 'Hello, client!',
            'details': 'This is a JSON message from the server.'
        }

        # Serialize the JSON data to a string
        json_string = json.dumps(json_data)

        # Send the JSON data to the client
        client_socket.sendall(json_string.encode('utf-8'))

        while True:
            # Receive data from the client
            received_data = client_socket.recv(1024)

            if not received_data:
                break  # Connection closed

            # Deserialize the received JSON data
            print("--- Got data.")
            # Send the received JSON data back to the client
            client_socket.sendall(json.dumps(json_data).encode('utf-8'))

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the client socket
        client_socket.close()
        print(f"Connection with {client_address} closed")