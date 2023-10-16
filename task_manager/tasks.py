import importlib.util
import sys
from pathlib import Path

from celery import Celery


app = Celery('tasks', broker='redis://localhost')
app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='Europe/Oslo',
    enable_utc=True,
    result_backend='redis://localhost'
)


class Constants:
    x = 10


@app.task
def start_exec(module_path: str, log_path: str) -> None:
    """Execute the main function of a submitted python file."""
    log_path = Path(log_path)

    spec = importlib.util.spec_from_file_location("tcp_motor", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    main_function = module.main

    old = sys.stdout
    with log_path.open(mode="w") as f:
        sys.stdout = f
        main_function()

    sys.stdout = old


@app.task
def sub():
    print("THIS IS SUB TASK")
    return 100
