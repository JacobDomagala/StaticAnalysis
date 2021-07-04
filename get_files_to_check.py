import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-exclude", help="Exclude prefix", required=False, default="")
parser.add_argument("-json", help="Compile commands file", required=True)

file_name = parser.parse_args().json
exclude_prefix = parser.parse_args().exclude
CHECK_FOR_PREFIX = len(exclude_prefix) > 0

with open(file_name, "r") as f:
    data = json.load(f)
    file_list = [
        p["file"]
        for p in data
        if not CHECK_FOR_PREFIX or not p["file"].startswith(exclude_prefix)
    ]
    for p in file_list:
        print(p)
