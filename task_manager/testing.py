from tasks import start_exec
import time
from celery.result import AsyncResult
import importlib.util


module_path = "../submissions/ESPLF/randomteam/LlN0ovTQ29uimTyTQMKu/LlN0ovTQ29uimTyTQMKu.py"
log_path = "../submissions/ESPLF/randomteam/LlN0ovTQ29uimTyTQMKu/LlN0ovTQ29uimTyTQMKu.log"
result = start_exec.delay(module_path, log_path)

# print("sleeping")
# time.sleep(5)
# print("done sleeping 5 seconds, terminating...")
# result.revoke(terminate=True)

print("done", result.get())
print(result.id)

# s = sub.delay()
# print(s.get())



# spec = importlib.util.spec_from_file_location("module_name", module_path)
# module = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(module)
# main_function = module.main
# r = main_function()
# print(r)