import socket
import json
import time


def stop_robot(ip_addr: str, port: int):
    # Define the server address and port
    server_address = (ip_addr, port)

    # Create a socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    sock.connect(server_address)

    try:
        for _ in range(2):
            # Listen for data from the server
            # input("Press enter to continue: ")
            data = sock.recv(1024).decode()

            if not data:
                # If the connection is closed, break out of the loop
                return False

            # Parse JSON data
            # received_data = json.loads(data)

            # Process the received data
            # For demonstration, let's just print the received data and send a response
            # print("----- Received Data:", received_data)
            motor_left, motor_right = 0, 0
            response_data = f'motor "{"f" if motor_left>0 else "b"}" "{abs(motor_left)}" "{"f" if motor_right>0 else "b"}" "{abs(motor_right)}"' + '\n'

            # Send the response back to the server
            print("xxxxx Sending data:", response_data)
            sock.send(response_data.encode("ascii"))

    except ConnectionResetError:
        print("Connection closed by the server.")
        return False
    
    except Exception as e:
        print(f"Error occurred: {e}")
        return False

    # Close the socket when done
    sock.close()
    return True