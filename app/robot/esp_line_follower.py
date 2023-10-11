import subprocess
import json

class ESPLineFollower():
    def __init__(self):
        # Configure ESP32's IP address and ports
        self.esp32_hostname = 'esp32'  # Replace with the ESP32's Hostname
        self.esp32_port = 8001         # Port for sending commands to ESP32
        self.esp32_sensor_port = 8002  # Port for obtaining sensor data from ESP32

    def connect(self):
        # Start socat as subprocess to establish the connection for sending commands
        self.socat_cmd = f'socat - tcp:{self.esp32_hostname}:{self.esp32_port}'
        self.socat_process = subprocess.Popen(
            self.socat_cmd, 
            shell=True, 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        print(f"Connected to {self.esp32_hostname}:{self.esp32_port} for sending commands")

        # Start socat subprocess for receiving sensor data
        self.socat_sensor_cmd = f'socat - tcp:{self.esp32_hostname}:{self.esp32_sensor_port}'
        self.socat_sensor_process = subprocess.Popen(
            self.socat_sensor_cmd, 
            shell=True, 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        print(f"Connected to {self.esp32_hostname}:{self.esp32_sensor_port} for sensor data")

    def run(self):
        try:
            while True:
                # Read the latest sensor data from the ESP32
                sensor_data = self.socat_sensor_process.stdout.readline().strip()

                # Find the last JSON object in the received data
                pos = sensor_data.rfind('{', 0, sensor_data.rfind('}') + 1)
                sensor_data = sensor_data[pos:]

                # Parse the JSON object
                sensor_data = json.loads(sensor_data)
                print(sensor_data, end='\n\n')

                # Process the sensor data and set motor values
                motor_left, motor_right = self.getMotorValues(sensor_data)

                # Send a message to the ESP32 to control motors
                message = f"motor {motor_left} {motor_right}"
                self.socat_process.stdin.write(message + '\n')
                self.socat_process.stdin.flush()

        except KeyboardInterrupt:
            print("Communication stopped.")

        finally:
            # Terminate socat subprocesses
            self.socat_process.terminate()
            self.socat_sensor_process.terminate()

    def getMotorValues(self, sensor_data):
        # Process the sensor data and set motor values

        '''
            Write your code here
        '''
        motor_left = self.base_speed
        motor_right = self.base_speed

        return motor_left, motor_right

# if __name__ == "__main__":
#     reRoIEEERAS = ESPLineFollower()
#     reRoIEEERAS.connect()
#     reRoIEEERAS.run()
