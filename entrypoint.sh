#!/bin/bash
# shellcheck disable=SC2155

set -e

export TERM=xterm-color

debug_print() {
    if [ "$INPUT_VERBOSE" = "true" ]; then
        IFS=$'\n' read -ra ADDR <<< "$1"
        for i in "${ADDR[@]}"; do
            echo -e "\u001b[32m $i"
        done
    fi
}

print_to_console=${INPUT_FORCE_CONSOLE_PRINT}

# Some debug info
debug_print "Using CMake = $INPUT_USE_CMAKE"
debug_print "Print to console = $print_to_console"

if [ $print_to_console = true ]; then
    echo "The 'force_console_print' option is enabled. Printing output to console."
elif [ -z "$INPUT_PR_NUM" ]; then
    echo "Pull request number input (pr_num) is not present. Printing output to console."
    print_to_console=true
else
    debug_print "Pull request number: ${INPUT_PR_NUM}"
fi

if [ -n "$INPUT_APT_PCKGS" ]; then
    apt-get update && eval apt-get install -y "$INPUT_APT_PCKGS"
fi

debug_print "Repo = ${INPUT_PR_REPO}  PR_HEAD = ${INPUT_PR_HEAD} event name = ${GITHUB_EVENT_NAME}"

use_extra_directory=false

# This is useful when running this Action from fork (together with [pull_request_target])
if [ "$GITHUB_EVENT_NAME" = "pull_request_target" ] && [ -n "$INPUT_PR_REPO" ]; then
    debug_print "Running in [pull_request_target] event! Cloning the Head repo ..."
    git clone "https://www.github.com/$INPUT_PR_REPO" pr_tree
    cd pr_tree || exit
    git checkout "$INPUT_PR_HEAD"
    use_extra_directory=true

    # Override commit SHA, in order to get the correct code snippet
    NEW_GITHUB_SHA=$(git rev-parse HEAD)
    export GITHUB_SHA=$NEW_GITHUB_SHA

    export GITHUB_WORKSPACE=$(pwd)
fi

debug_print "GITHUB_WORKSPACE = ${GITHUB_WORKSPACE} INPUT_EXCLUDE_DIR = ${INPUT_EXCLUDE_DIR} use_extra_directory = ${use_extra_directory}"

if [ -n "$INPUT_INIT_SCRIPT" ]; then
    chmod +x "$INPUT_INIT_SCRIPT"
    # shellcheck source=/dev/null
    source "$INPUT_INIT_SCRIPT"
fi

mkdir -p build && cd build || exit

if [ $INPUT_USE_CMAKE = true ]; then
    cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON "$INPUT_CMAKE_ARGS" ..
fi

if [ -z "$INPUT_EXCLUDE_DIR" ]; then
    files_to_check=$(python3 /get_files_to_check.py -dir="$GITHUB_WORKSPACE")
    debug_print "Running: files_to_check=python3 /get_files_to_check.py -dir=\"$GITHUB_WORKSPACE\")"
else
    files_to_check=$(python3 /get_files_to_check.py -exclude="$GITHUB_WORKSPACE/$INPUT_EXCLUDE_DIR" -dir="$GITHUB_WORKSPACE")
    debug_print "Running: files_to_check=python3 /get_files_to_check.py -exclude=\"$GITHUB_WORKSPACE/$INPUT_EXCLUDE_DIR\" -dir=\"$GITHUB_WORKSPACE\")"
fi

debug_print "Files to check = $files_to_check"
debug_print "INPUT_CPPCHECK_ARGS = $INPUT_CPPCHECK_ARGS"
debug_print "INPUT_CLANG_TIDY_ARGS = $INPUT_CLANG_TIDY_ARGS"

if [ $INPUT_USE_CMAKE = true ]; then
    if [ -z "$INPUT_EXCLUDE_DIR" ]; then
        debug_print "Running cppcheck --project=compile_commands.json $INPUT_CPPCHECK_ARGS --output-file=cppcheck.txt ..."
        eval cppcheck --project=compile_commands.json "$INPUT_CPPCHECK_ARGS" --output-file=cppcheck.txt
    else
        debug_print "Running cppcheck --project=compile_commands.json $INPUT_CPPCHECK_ARGS --output-file=cppcheck.txt -i$GITHUB_WORKSPACE/$INPUT_EXCLUDE_DIR ..."
        eval cppcheck --project=compile_commands.json "$INPUT_CPPCHECK_ARGS" --output-file=cppcheck.txt -i"$GITHUB_WORKSPACE/$INPUT_EXCLUDE_DIR"
    fi
else
    # Excludes for clang-tidy are handled in python script
    debug_print "Running cppcheck $files_to_check $INPUT_CPPCHECK_ARGS --output-file=cppcheck.txt ..."
    eval cppcheck $files_to_check "$INPUT_CPPCHECK_ARGS" --output-file=cppcheck.txt
fi

# Excludes for clang-tidy are handled in python script
debug_print "Running clang-tidy-15 $INPUT_CLANG_TIDY_ARGS -p $(pwd) $files_to_check >>clang_tidy.txt 2>&1"
eval clang-tidy-15 "$INPUT_CLANG_TIDY_ARGS" -p "$(pwd)" "$files_to_check" >>clang_tidy.txt 2>&1 || true

python3 /run_static_analysis.py -cc cppcheck.txt -ct clang_tidy.txt -o $print_to_console -fk $use_extra_directory
