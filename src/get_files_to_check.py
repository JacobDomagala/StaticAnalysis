import argparse
from pathlib import Path


def get_files_to_check(directory_in, excludes_in):
    exclude_prefixes = [f"{directory_in}/build"]

    if excludes_in is not None:
        excludes_list = excludes_in.split(" ")
        for exclude in excludes_list:
            exclude_prefixes.append(str(exclude))

    supported_extensions = (".h", ".hpp", ".hcc", ".c", ".cc", ".cpp", ".cxx")
    all_files = []

    for path in Path(directory_in).rglob("*.*"):
        path_ = str(path.resolve())
        if path_.endswith(supported_extensions) and not path_.startswith(
            tuple(exclude_prefixes)
        ):
            all_files.append(path_)

    return " ".join(all_files)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-exclude", help="Exclude prefix", required=False)
    parser.add_argument("-dir", help="Current directory", required=True)

    directory = parser.parse_args().dir
    excludes = parser.parse_args().exclude

    print(get_files_to_check(directory, excludes))
