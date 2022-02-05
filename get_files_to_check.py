import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("-exclude", help="Exclude prefix", required=False)
parser.add_argument("-dir", help="Current directory", required=True)

directory = parser.parse_args().dir
exclude_prefixes = [f"{directory}/build"]
if parser.parse_args().exclude:
    exclude_prefixes.append(str(parser.parse_args().exclude))
supported_extensions = (".h", ".hpp", ".hcc", ".c", ".cc", ".cpp", ".cxx")
all_files = []

for path in Path(directory).rglob("*.*"):
    PATH = str(path.resolve())
    if PATH.endswith(supported_extensions) and not PATH.startswith(
        tuple(exclude_prefixes)
    ):
        all_files.append(PATH)

print(" ".join(all_files))
