# -*- coding: utf-8 -*-
import sys
import time

import tomli
import tomli_w

STABLE_VERSION = [
    "0.1.0",
]


def version(tag: str = "test") -> str:
    match tag:
        case "test":
            current_time = time.localtime()
            time_str_ = f"{current_time.tm_year:04d}.{current_time.tm_mon:02d}.{current_time.tm_mday:02d}.{current_time.tm_hour:02d}{current_time.tm_min:02d}"
            version_name = time_str_
        case "stable":
            current_time = time.localtime()
            version_name = STABLE_VERSION[-1]
        case _:
            raise ValueError(
                f"Unknown tag: {tag}, expected 'test' or 'stable'."
            )
    return version_name


if __name__ == "__main__":

    argc = len(sys.argv)
    argv = sys.argv

    current_version = version(argv[1] if argc > 1 else "test")

    with open("pyproject.toml", "rb") as f:
        meta = tomli.load(f)
        meta["project"]["version"] = current_version

    with open("pyproject.toml", "wb") as f2:
        tomli_w.dump(meta, f2)

    print(f"Version updated to {current_version} in pyproject.toml")
    pass
