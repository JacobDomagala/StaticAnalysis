import argparse
from pathlib import Path


def get_files_to_check(directory_in, excludes_in, preselected_files, lang):
    """
    Given a directory path and a string of prefixes to exclude,
    return a space-separated string of all files in the directory (and its subdirectories)
    that have a supported extension and do not start with any of the excluded prefixes.

    Args:
        directory_in (str): The path to the directory to search for files.
        excludes_in (str): A space-separated string of prefixes to exclude from the search.
        preselected_files (str): If present, then it's the list of files to be checked (minus excluded ones)
        lang (str): Programming language

    Returns:
        str: A space-separated string of file paths that meet the search criteria.
    """

    exclude_prefixes = [f"{directory_in}/build"]

    if excludes_in is not None:
        excludes_list = excludes_in.split(" ")
        for exclude in excludes_list:
            exclude_prefixes.append(str(exclude))

    if lang == "c++":
        supported_extensions = (".h", ".hpp", ".hcc", ".c", ".cc", ".cpp", ".cxx")
    elif lang == "python":
        supported_extensions = ".py"
    else:
        raise RuntimeError(f"Unknown language {lang}")

    all_files = []

    if len(preselected_files) == 0:
        for path in Path(directory_in).rglob("*.*"):
            path_ = str(path.resolve())
            if path_.endswith(supported_extensions) and not path_.startswith(
                tuple(exclude_prefixes)
            ):
                all_files.append(path_)
    else:
        for file in preselected_files:
            if not file.startswith(directory_in):
                file = f"{directory_in}/{file}"
            if not file.startswith(tuple(exclude_prefixes)):
                all_files.append(file)

    return " ".join(all_files)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-exclude", help="Exclude prefix", required=False)
    parser.add_argument(
        "-preselected", help="Preselected files", default="", required=False
    )
    parser.add_argument("-dir", help="Source directory", required=True)
    parser.add_argument("-lang", help="Programming language", required=True)

    directory = parser.parse_args().dir
    preselected = parser.parse_args().preselected
    excludes = parser.parse_args().exclude
    language = parser.parse_args().lang

    print(get_files_to_check(directory, excludes, preselected.split(), language))
