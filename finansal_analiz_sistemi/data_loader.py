import runpy

if __name__ == "__main__":
    runpy.run_module("data_loader", run_name="__main__")
else:
    from data_loader import *  # noqa: F401,F403
