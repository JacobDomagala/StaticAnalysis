#!/bin/bash
# shellcheck disable=SC2155

set -e
set -x
# Following variables are declared/defined in parent script
preselected_files=${preselected_files:-""}
print_to_console=${print_to_console:-false}
use_extra_directory=${use_extra_directory:-false}
common_ancestor=${common_ancestor:-""}

if [ -z "$INPUT_PYTHON_DIRS" ]; then
    debug_print "Error: python_dirs action input is empty! You have to provide directories that contain python files to be checked."
    exit 1
fi

if [ -z "$INPUT_EXCLUDE_DIR" ]; then
    files_to_check=$(python3 /get_files_to_check.py -dir="$GITHUB_WORKSPACE" -preselected="$preselected_files" -lang="python")
    debug_print "Running: files_to_check=python3 /get_files_to_check.py -dir=\"$GITHUB_WORKSPACE\" -preselected=\"$preselected_files\")"
else
    files_to_check=$(python3 /get_files_to_check.py -exclude="$GITHUB_WORKSPACE/$INPUT_EXCLUDE_DIR" -dir="$GITHUB_WORKSPACE" -preselected="$preselected_files")
    debug_print "Running: files_to_check=python3 /get_files_to_check.py -exclude=\"$GITHUB_WORKSPACE/$INPUT_EXCLUDE_DIR\" -dir=\"$GITHUB_WORKSPACE\" -preselected=\"$preselected_files\")"
fi

debug_print "Files to check = $files_to_check"

if [ -z "$files_to_check" ]; then
    echo "No files to check"
else
    pip3 install pylint --break-system-packages

    # Trim newlines
    INPUT_PYLINT_ARGS="${INPUT_PYLINT_ARGS%"${INPUT_PYLINT_ARGS##*[![:space:]]}"}"
    eval "pylint $INPUT_PYTHON_DIRS --output-format=json:pylint_out.json $INPUT_PYLINT_ARGS || true"
    python3 /static_analysis_python.py -pl ./pylint_out.json -o "$print_to_console" -fk "$use_extra_directory" --common "$common_ancestor" --head "origin/$GITHUB_HEAD_REF"
fi
