import typing


def get_motor_values(sensor_data) -> typing.Tuple[int, int]:
    """
    Pass sensor data from main() to get_motor_values.

    Sensor_data sample:
    {'s1': 1, 's2': 1, 's3': 1, 's4': 1, 's5': 1}
    """
    print(f"Got sensor Data: {sensor_data}")
    return 10, 10  # sample motor left and motor right PWM values.

def main(ip_addr, port) -> None:
    pass