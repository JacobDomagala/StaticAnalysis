#!/bin/bash

set -x

print_to_console=${INPUT_FORCE_CONSOLE_PRINT}

if [ -n "$INPUT_FORCE_CONSOLE_PRINT"]; then
    echo "The 'force_console_print' option is enabled. Printing output to console."
elif [ -z "$INPUT_PR_NUM" ]; then
    echo "Pull request number input is not present. Printing output to console."
    print_to_console=true
else
    echo "Pull request numer is ${INPUT_PR_NUM}"
fi

if [ -n "$INPUT_APT_PCKGS" ]; then
    apt-get update && eval apt-get install -y "$INPUT_APT_PCKGS"
fi

if [ -n "$INPUT_INIT_SCRIPT" ]; then
    chmod +x "$INPUT_INIT_SCRIPT"
    # shellcheck source=/dev/null
    source "$INPUT_INIT_SCRIPT"
fi

mkdir build && cd build || exit
cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON "$INPUT_CMAKE_ARGS" ..

files_to_check=$(python3 /get_files_to_check.py -exclude="$INPUT_EXCLUDE_DIR" -json="compile_commands.json")

if [ -z "$INPUT_EXCLUDE_DIR" ]; then
    eval cppcheck --project=compile_commands.json "$INPUT_CPPCHECK_ARGS" --output-file=cppcheck.txt
else
    eval cppcheck --project=compile_commands.json "$INPUT_CPPCHECK_ARGS" --output-file=cppcheck.txt -i"$GITHUB_WORKSPACE/$INPUT_EXCLUDE_DIR"
fi

# Excludes for clang-tidy are handled in python script
eval clang-tidy-12 "$INPUT_CLANG_TIDY_ARGS" -p "$(pwd)" "$files_to_check" -- >"clang_tidy.txt"

python3 /run_static_analysis.py -cc cppcheck.txt -ct clang_tidy.txt
