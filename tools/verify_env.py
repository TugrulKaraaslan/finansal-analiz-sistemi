import sys
import numpy as np

if int(np.__version__.split(".")[0]) >= 2:
    sys.exit("NumPy >= 2.0 detected, aborting.")
