import socket
import json
import time


def main():
    # Define the server address and port
    server_address = ('127.0.0.1', 8002)

    # Create a socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    sock.connect(server_address)

    for _ in range(5):
        try:
            # Listen for data from the server
            # input("Press enter to continue: ")
            time.sleep(2)
            data = sock.recv(1024).decode()

            if not data:
                # If the connection is closed, break out of the loop
                break

            try:
                # Parse JSON data
                received_data = json.loads(data)

                # Process the received data
                # For demonstration, let's just print the received data and send a response
                print("----- Received Data:", received_data)

                # Prepare a response
                motor_left = 10
                motor_right = 10
                response_data = f"motor {motor_left} {motor_right}\n"

                # Send the response back to the server
                print("xxxxx Sending data:", response_data)
                sock.send(response_data.encode())

            except json.JSONDecodeError as e:
                print("Error parsing JSON:", e)

        except ConnectionResetError:
            print("Connection closed by the server.")
            break

    # Close the socket when done
    sock.close()
