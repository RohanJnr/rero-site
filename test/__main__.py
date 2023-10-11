import importlib

module = importlib.import_module("client")  # dynamic ID.
motor = module.motor

if len(dir(motor)) > 9:
    print("imports detected!")
else:
    print("no imports")

