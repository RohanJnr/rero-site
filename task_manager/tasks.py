import importlib.util
import requests
import socket
import sys
import traceback
from pathlib import Path
from threading import Thread

import redis
from celery import Celery
from celery.app.task import Context
from celery.signals import task_postrun, task_revoked

from app.models import APITaskFinished
from task_manager.utils import stop_robot


ESP_IP_ADDR = 'localhost'
ESP_PORT = 12345
BACKEND_ROUTE = "http://localhost:8000"


app = Celery('tasks', broker='redis://localhost')
app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='Europe/Oslo',
    enable_utc=True,
    result_backend='redis://localhost'
)


@app.task
def start_exec(*, code: str, module_path: str, log_path: str, **kwargs) -> None:
    """Execute the main function of a submitted python file."""

    module_path = Path(module_path)
    log_path = Path(log_path)


    module_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    module_path.touch()
    log_path.touch()

    module_path.write_text(code)

    old = sys.stdout
    with log_path.open(mode="w") as f:
        sys.stdout = f
        try:
            spec = importlib.util.spec_from_file_location("tcp_motor", module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            main_function = module.main
            main_function(ESP_IP_ADDR, ESP_PORT)

        except Exception as e:
            trace = traceback.format_exc()
            print(f"Error: {e}\nTraceback:\n{trace}")
        finally:
            sys.stdout = old


@app.task
def start_controls():
    """Start manual controls."""
    server_address = (ESP_IP_ADDR, ESP_PORT)
    # Create a socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("connected.")
    # Connect to the server
    sock.connect(server_address)

    data = sock.recv(1024)

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


@task_postrun.connect
def task_postrun_handler(sender=None, headers=None, body=None, **kwargs) -> None:
    """Handle post task run."""
    print("Task Post Run.")
    p = Thread(target=stop_robot, args=(ESP_IP_ADDR, ESP_PORT))
    p.start()
    p.join(timeout=15)
    # result = stop_robot(ESP_IP_ADDR, ESP_PORT)
    # if not result:
    #     print("Couldn't stop ESP Robot, please stop it manually!")

    ctx: Context = sender.request
    metadata = ctx.kwargs.get("metadata", None)
    log_path = ctx.kwargs.get("log_path", None)
    if not metadata or not log_path:
        return
    log_path = Path(log_path)
    logs = log_path.read_text()

    data = APITaskFinished(submission_id=metadata["submission_id"], log_path=str(log_path), logs=logs)
    headers = {
        "Content-Type": "application/json"
    }
    r = requests.post(f"{BACKEND_ROUTE}/api/submission/task_finished", json=data.model_dump(), headers=headers)
    print(r.status_code)
    print(r.text)


@task_revoked.connect
def task_revoked_handler(sender=None, headers=None, body=None, **kwargs) -> None:
    """Handle post task run."""
    print(sender)
    print("Cancelling task...")
    p = Thread(target=stop_robot, args=(ESP_IP_ADDR, ESP_PORT))
    p.start()
    p.join(timeout=15)
    # result = stop_robot(ESP_IP_ADDR, ESP_PORT)
    # if not result:
    #     print("Couldn't stop ESP Robot, please stop it manually!")

    print("Task Cancelled.")
    # ctx: Context = sender.request
    req: Context = kwargs['request']
    metadata = req.kwargs.get("metadata", None)
    log_path = req.kwargs.get("log_path", None)
    if not metadata or not log_path:
        return
    log_path = Path(log_path)
    logs = log_path.read_text()

    data = APITaskFinished(submission_id=metadata["submission_id"], log_path=str(log_path), logs=logs)
    headers = {
        "Content-Type": "application/json"
    }
    r = requests.post(f"{BACKEND_ROUTE}/api/submission/task_finished", json=data.model_dump(), headers=headers)
    print(r.status_code)