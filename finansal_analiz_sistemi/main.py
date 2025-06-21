import runpy

if __name__ == "__main__":
    runpy.run_module("run", run_name="__main__")
else:
    from run import *  # noqa: F401,F403
