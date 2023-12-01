#!/bin/bash
# shellcheck disable=SC2155

set -e
set -x
# Following variables are declared/defined in parent script
preselected_files=${preselected_files:-""}
print_to_console=${print_to_console:-false}
use_extra_directory=${use_extra_directory:-false}
common_ancestor=${common_ancestor:-""}

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
    pylint . --output-format=json:pylint_out.json || true
    python3 /python/run_static_analysis.py -pl ./pylint_out.json -o "$print_to_console" -fk "$use_extra_directory" --common "$common_ancestor" --head "origin/$GITHUB_HEAD_REF"
fi
