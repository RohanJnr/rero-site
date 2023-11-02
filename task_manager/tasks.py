import importlib.util
import requests
import sys
import traceback
from pathlib import Path

from celery import Celery
from celery.app.task import Context
from celery.signals import task_postrun

from app.models import APITaskFinished
from task_manager.utils import stop_robot


ESP_IP_ADDR = '192.168.0.105'
ESP_PORT = 8002
BACKEND_ROUTE = "http://20.197.11.23:8000"


app = Celery('tasks', broker='redis://20.197.11.23')
app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='Europe/Oslo',
    enable_utc=True,
    result_backend='redis://20.197.11.23'
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


@task_postrun.connect
def task_postrun_handler(sender=None, headers=None, body=None, **kwargs) -> None:
    """Handle post task run."""
    result = stop_robot(ESP_IP_ADDR, ESP_PORT)
    if not result:
        print("Couldn't stop ESP Robot, please stop it manually!")

    print("Task Done.")

    ctx: Context = sender.request
    metadata = ctx.kwargs.get("metadata", None)
    log_path = ctx.kwargs.get("log_path", None)

    log_path = Path(log_path)

    logs = log_path.read_text()

    data = APITaskFinished(submission_id=metadata["submission_id"], task_id=ctx.id, log_path=str(log_path), logs=logs)
    headers = {
        "Content-Type": "application/json"
    }
    r = requests.post(f"{BACKEND_ROUTE}/api/submission/task_finished", json=data.model_dump(), headers=headers)
    print(r.status_code)