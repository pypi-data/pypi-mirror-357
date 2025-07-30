import sys

import mzcst_2024 as mz

if __name__ == "__main__":
    for i, p in enumerate(sys.path):
        print(f"{i:2d}: {p}")
    # print(sys.path)
    print(mz.__version__)
    print(mz.__file__)   

    pass
