'''
    IEEE RAS

    Author: Pratham Bhat
    Date: 19-09-2023

    This is the base code for the Remote Robotics Lab IOT robot.

    INSTRUCTIONS:
        - Join the Husarnet network using the credentials provided by the lab on your device.
        - Replace the hostname with your team name in the format: team-<team_number> in the __init__ function
        - Replace the port numbers with the port numbers provided by the lab in the __init__ function
        - Write your code in the getMotorValues function
        - Run this code using the command: 
            linux   -> python3 base.py
            windows -> python base.py

    Warnings:
        - Do not change the code anywhere other than the getMotorValues function and the hostname and port numbers
        - Do not attempt this in a virtual machine since the ports will not be accessible unless port forwarding is done
'''

import json
import time
import socket

class LineFollower():
    def __init__(self, ip, port):
        # Configure ESP32's IP address and ports
        self.esp32_hostname = ip  # Replace with the ESP32's Hostname
        # self.esp32_hostname = '192.168.212.149'  # Replace with the ESP32's Hostname
        # self.esp32_hostname = '192.168.212.9'  # Replace with the ESP32's Hostname
        # self.esp32_hostname = "esp32"
        # self.esp32_hostname = "fc94:4c06:9351:8fea:9d09:7dc4:6266:c5dc"
        self.esp32_sensor_port = port  # Port for obtaining sensor data from ESP32

        # Configure motor speeds
        self.base_speed = 50                             # Base speed for motors
        self.turn_speed = round(self.base_speed * 0.75)          # Speed for motors when the robot is turning
        self.boost_speed = round(self.turn_speed * 1.75)        # Speed boost for motors when the line is detected by the mild sensors
        self.ultra_boost_speed = round(self.turn_speed * 2.75)  # Speed boost for motors when the line is detected by the extreme sensors
        # config = [[0.5, 1.75, 2.75], [0.75, 1, 1.01]][0]
        # self.turn_speed, self.boost_speed, self.ultra_boost_speed = [self.base_speed * i for i in config]

    def connect(self):
        # Create socket for receiving sensor data
        self.sensor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.sensor_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.sensor_socket.connect((self.esp32_hostname, self.esp32_sensor_port))

        print(f"Connected to {self.esp32_hostname}:{self.esp32_sensor_port} for sensor data")

    def run(self):
        try:
            while True:
                time.sleep(0.1)
                # Read the latest sensor data from the ESP32
                sensor_data = self.sensor_socket.recv(1024).decode().strip()

                if not sensor_data:
                    continue

                print(sensor_data)

                # Find the last JSON object in the received data
                # pos = sensor_data.rfind('{', 0, sensor_data.rfind('}') + 1)
                # sensor_data = sensor_data[pos:]

                try:
                    # Parse the JSON object
                    sensor_data = json.loads(sensor_data)
                    # print(sensor_data, end='\n\n')
                except json.decoder.JSONDecodeError:
                    print("JSONDecodeError")
                    print(sensor_data)
                    continue

                # Process the sensor data and set motor values
                motor_left, motor_right = self.getMotorValues(sensor_data)

                # Send a message to the ESP32 to control motors
                message = f'motor "{"f" if motor_left>0 else "b"}" "{abs(motor_left)}" "{"f" if motor_right>0 else "b"}" "{abs(motor_right)}"' + '\n'
                self.sensor_socket.send(message.encode('ascii'))
                print(message)

        except KeyboardInterrupt:
            message = f'motor "f" "0" "f" "0"' + '\n'
            self.sensor_socket.send(message.encode())
            print(message)

            time.sleep(0.1)

            sensor_data = self.sensor_socket.recv(1024).decode().strip()
            message = f'motor "f" "0" "f" "0"' + '\n'
            self.sensor_socket.send(message.encode())
            print(message)

            time.sleep(0.1)
            print("Communication stopped.")

        finally:

            self.sensor_socket.close()
            print("Terminated sensor socket")

    def getMotorValues(self, sensor_data):
        # Process the sensor data and set motor values
        # The speeds of the motors is increased according to the sensor data to center the robot on the line
        if(sensor_data['s1']):
            motor_left = self.turn_speed
            motor_right = self.ultra_boost_speed
        elif(sensor_data['s2']):
            motor_left = self.turn_speed
            motor_right = self.boost_speed
        elif(sensor_data['s4']):
            motor_left = self.boost_speed
            motor_right = self.turn_speed
        elif(sensor_data['s5']):
            motor_left = self.ultra_boost_speed
            motor_right = self.turn_speed
        elif(sensor_data['s3']):
            motor_left = self.base_speed
            motor_right = self.base_speed
        else:
            motor_left = -self.base_speed
            motor_right = -self.base_speed

        return motor_left, motor_right

def main(ip, port):
    lineFollower = LineFollower(ip, port)
    lineFollower.connect()
    lineFollower.run()