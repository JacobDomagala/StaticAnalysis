import argparse
from pathlib import Path


def _normalize_path(path_in, base_directory):
    path = Path(path_in)
    if not path.is_absolute():
        path = Path(base_directory) / path
    return str(path.resolve())


def _matches_include_prefixes(path_in, include_prefixes):
    return len(include_prefixes) == 0 or path_in.startswith(tuple(include_prefixes))


def get_files_to_check(
    directory_in, excludes_in, preselected_files, lang, include_dirs_in=None
):
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

    directory = str(Path(directory_in).resolve())
    exclude_prefixes = [f"{directory}/build"]

    if excludes_in is not None:
        excludes_list = excludes_in.split()
        for exclude in excludes_list:
            exclude_prefixes.append(_normalize_path(exclude, directory))

    include_prefixes = []
    if include_dirs_in:
        include_dirs_list = include_dirs_in.split()
        for include_dir in include_dirs_list:
            include_prefixes.append(_normalize_path(include_dir, directory))

    if lang == "c++":
        supported_extensions = (".h", ".hpp", ".hcc", ".c", ".cc", ".cpp", ".cxx")
    elif lang == "python":
        supported_extensions = ".py"
    else:
        raise RuntimeError(f"Unknown language {lang}")

    all_files = []

    if len(preselected_files) == 0:
        for path in Path(directory).rglob("*.*"):
            path_ = str(path.resolve())
            if (
                path_.endswith(supported_extensions)
                and not path_.startswith(tuple(exclude_prefixes))
                and _matches_include_prefixes(path_, include_prefixes)
            ):
                all_files.append(path_)
    else:
        if isinstance(preselected_files, str):
            preselected_files = preselected_files.split()

        for file in preselected_files:
            file = _normalize_path(file, directory)
            if not file.startswith(tuple(exclude_prefixes)) and _matches_include_prefixes(
                file, include_prefixes
            ):
                all_files.append(file)

    return " ".join(all_files)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-exclude", help="Exclude prefix", required=False)
    parser.add_argument(
        "-include", help="Directories to include (space separated)", required=False
    )
    parser.add_argument(
        "-preselected", help="Preselected files", default="", required=False
    )
    parser.add_argument("-dir", help="Source directory", required=True)
    parser.add_argument("-lang", help="Programming language", required=True)

    args = parser.parse_args()

    print(
        get_files_to_check(
            args.dir, args.exclude, args.preselected.split(), args.lang, args.include
        )
    )
