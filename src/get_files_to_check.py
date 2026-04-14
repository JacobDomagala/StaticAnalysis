import argparse
from pathlib import Path


def _normalize_path(path_in, base_directory):
    path = Path(path_in)
    if not path.is_absolute():
        path = Path(base_directory) / path
    return str(path.resolve())


def _matches_include_prefixes(path_in, include_prefixes):
    return (not include_prefixes) or path_in.startswith(tuple(include_prefixes))


def _build_prefixes(directory, raw_prefixes):
    if not raw_prefixes:
        return []
    return [_normalize_path(prefix, directory) for prefix in raw_prefixes.split()]


def _get_supported_extensions(lang):
    if lang == "c++":
        return (".h", ".hpp", ".hcc", ".c", ".cc", ".cpp", ".cxx")
    if lang == "python":
        return ".py"
    raise RuntimeError(f"Unknown language {lang}")


def _normalize_preselected(preselected_files, directory):
    if isinstance(preselected_files, str):
        preselected_files = preselected_files.split()
    return [_normalize_path(file_path, directory) for file_path in preselected_files]


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
    exclude_prefixes = [f"{directory}/build", *_build_prefixes(directory, excludes_in)]
    include_prefixes = _build_prefixes(directory, include_dirs_in)
    supported_extensions = _get_supported_extensions(lang)

    all_files = []

    if not preselected_files:
        for path in Path(directory).rglob("*.*"):
            path_ = str(path.resolve())
            if (
                path_.endswith(supported_extensions)
                and not path_.startswith(tuple(exclude_prefixes))
                and _matches_include_prefixes(path_, include_prefixes)
            ):
                all_files.append(path_)
    else:
        for file_path in _normalize_preselected(preselected_files, directory):
            if not file_path.startswith(
                tuple(exclude_prefixes)
            ) and _matches_include_prefixes(file_path, include_prefixes):
                all_files.append(file_path)

    all_files.sort()

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
