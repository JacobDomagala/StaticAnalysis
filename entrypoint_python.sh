#!/bin/bash
# shellcheck disable=SC2155

set -e

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
    debug_print "Running: files_to_check=\$(python3 /src/get_files_to_check.py -dir=\"$GITHUB_WORKSPACE\" -preselected=\"$preselected_files\" -lang=\"python\")"
    files_to_check=$(python3 /src/get_files_to_check.py -dir="$GITHUB_WORKSPACE" -preselected="$preselected_files" -lang="python")
else
    debug_print "Running: files_to_check=\$(python3 /src/get_files_to_check.py -exclude=\"$GITHUB_WORKSPACE/$INPUT_EXCLUDE_DIR\" -dir=\"$GITHUB_WORKSPACE\" -preselected=\"$preselected_files\" -lang=\"python\")"
    files_to_check=$(python3 /src/get_files_to_check.py -exclude="$GITHUB_WORKSPACE/$INPUT_EXCLUDE_DIR" -dir="$GITHUB_WORKSPACE" -preselected="$preselected_files" -lang="python")
fi

debug_print "Files to check = $files_to_check"

if [ -z "$files_to_check" ]; then
    echo "No files to check"
else
    # Trim newlines
    INPUT_PYLINT_ARGS="${INPUT_PYLINT_ARGS%"${INPUT_PYLINT_ARGS##*[![:space:]]}"}"
    eval "pylint $files_to_check --output-format=json:pylint_out.json $INPUT_PYLINT_ARGS || true"

    cd /
    python3 -m src.static_analysis_python -pl "$GITHUB_WORKSPACE/pylint_out.json" -o "$print_to_console" -fk "$use_extra_directory" --common "$common_ancestor" --head "origin/$GITHUB_HEAD_REF"
fi
