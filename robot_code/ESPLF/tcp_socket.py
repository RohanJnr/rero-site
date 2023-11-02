import socket
import json
import time


def getMotorValues(sensor_data):
    # Process the sensor data and set motor values
    # The speeds of the motors is increased according to the sensor data to center the robot on the line

    base_speed = 20
    turn_speed = base_speed * 0.5
    boost_speed = turn_speed * 1.75
    ultra_boost_speed = turn_speed * 2.75

    if(sensor_data['s1']):
        motor_left = turn_speed
        motor_right = ultra_boost_speed
    elif(sensor_data['s2']):
        motor_left = turn_speed
        motor_right = boost_speed
    elif(sensor_data['s4']):
        motor_left = boost_speed
        motor_right = turn_speed
    elif(sensor_data['s5']):
        motor_left = ultra_boost_speed
        motor_right = turn_speed
    elif(sensor_data['s3']):
        motor_left = base_speed
        motor_right = base_speed
    else:
        motor_left = -base_speed
        motor_right = -base_speed

    return round(motor_left), round(motor_right)


def main():
    # Define the server address and port
    server_address = ('192.168.0.105', 8002)

    # Create a socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    sock.connect(server_address)

    for i in range(5):
        try:
            # Listen for data from the server
            # input("Press enter to continue: ")
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
                # if i == 4:
                #     motor_left = 0
                #     motor_right = 0
                # elif i==3:
                #     motor_left = 100
                #     motor_right = 0
                # else:
                #     motor_left = 0
                #     motor_right = 100
                motor_left, motor_right = getMotorValues(received_data)
                response_data = f'motor "{"f" if motor_left>0 else "b"}" "{abs(motor_left)}" "{"f" if motor_right>0 else "b"}" "{abs(motor_right)}"' + '\n'
                # response_data = f"motor {motor_left} {motor_right}\n"

                # Send the response back to the server
                print("xxxxx Sending data:", response_data)
                sock.send(response_data.encode("ascii"))
                # time.sleep(2)

            except json.JSONDecodeError as e:
                print("Error parsing JSON:", e)
                print(f"data: {data}")

        except ConnectionResetError:
            print("Connection closed by the server.")
            break

    # Close the socket when done
    sock.close()
