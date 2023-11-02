import socket
import redis


ESP_IP_ADDR = '192.168.0.101'
ESP_PORT = 8002


def start_controls():
    """Start manual controls."""
    server_address = (ESP_IP_ADDR, ESP_PORT)
    # Create a socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("connected.")
    # Connect to the server
    sock.connect(server_address)

    data = sock.recv(1024)
    print(data)

    redis_conn = redis.Redis()

    pubsub = redis_conn.pubsub()
    pubsub.subscribe("controls")
    print("Listening for messages.")

    match_dict = {
        'w': 'motor "f" "30" "f" "30"\n',
        'a': 'motor "b" "30" "f" "30"\n',
        's': 'motor "b" "30" "b" "30"\n',
        'd': 'motor "f" "30" "b" "30"\n',
        'x': 'motor "f" "0" "f" "0"\n',
    }

    for message in pubsub.listen():
        print(f"Received message: {message}")
        if message["type"] == "message":
            key = message["data"].decode()
            val = match_dict.get(key, None)
            if val:
                print(f"Sending {val}")
                sock.send(val.encode("ascii"))
                data = sock.recv(1024)
                print(data)
            else:
                print("no value.")

start_controls()