import os
import sys

if __name__ == "__main__":
    mzcst_path = "../src"
    abspath = os.path.abspath(mzcst_path)
    print(f"Adding {abspath} to sys.path")
    sys.path.append(abspath)

    # This is a demo script to show how to use mzcst
    for i, p in enumerate(sys.path):
        print(f"{i:2d}: {p}")
    import mzcst_2024 as mz

    print(mz.__version__)
    print(mz.__file__)

    pass
