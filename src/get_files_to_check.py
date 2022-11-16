import argparse
from pathlib import Path

def get_files_to_check(directory, excludes):
    exclude_prefixes = [f"{directory}/build"]

    if excludes != None:
        excludes = excludes.split(" ")
        for exclude in excludes:
            exclude_prefixes.append(str(exclude))

    supported_extensions = (".h", ".hpp", ".hcc", ".c", ".cc", ".cpp", ".cxx")
    all_files = []

    for path in Path(directory).rglob("*.*"):
        PATH = str(path.resolve())
        if PATH.endswith(supported_extensions) and not PATH.startswith(
            tuple(exclude_prefixes)
        ):
            all_files.append(PATH)

    return " ".join(all_files)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-exclude", help="Exclude prefix", required=False)
    parser.add_argument("-dir", help="Current directory", required=True)

    directory = parser.parse_args().dir
    excludes = parser.parse_args().exclude

    print(get_files_to_check(directory, excludes))