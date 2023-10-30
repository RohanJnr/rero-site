import importlib.util
import requests
import sys
import traceback
from pathlib import Path

from celery import Celery
from celery.app.task import Context
from celery.signals import task_postrun

from app.models import APITaskFinished


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
def start_exec(*, module_path: str, log_path: str, **kwargs) -> None:
    """Execute the main function of a submitted python file."""
    log_path = Path(log_path)

    old = sys.stdout
    with log_path.open(mode="w") as f:
        sys.stdout = f
        try:
            spec = importlib.util.spec_from_file_location("tcp_motor", module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            main_function = module.main
            main_function()

        except Exception as e:
            trace = traceback.format_exc()
            print(f"Error: {e}\nTraceback:\n{trace}")
        finally:
            sys.stdout = old


@task_postrun.connect
def task_postrun_handler(sender=None, headers=None, body=None, **kwargs) -> None:
    """Handle post task run."""
    print("Task Done.")

    ctx: Context = sender.request
    metadata = ctx.kwargs.get("metadata", None)
    log_path = ctx.kwargs.get("log_path", None)

    data = APITaskFinished(submission_id=metadata["submission_id"], task_id=ctx.id, log_path=log_path)
    headers = {
        "Content-Type": "application/json"
    }
    r = requests.post("http://localhost:8000/api/submission/task_finished", json=data.model_dump(), headers=headers)
    print(r.status_code)