#!/bin/bash

set -x

if [ "$INPUT_PR_NUM" == "null" ]; then
  echo "Pull request number input is not present! This action can only run on Pull Requests!"
  exit 0
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

if [ -z "$INPUT_EXCLUDE_DIR" ]; then
    eval cppcheck --project=compile_commands.json "$INPUT_CPPCHECK_ARGS" --output-file=cppcheck.txt
    run-clang-tidy-12 -- >(tee "clang_tidy.txt")
else
    eval cppcheck --project=compile_commands.json "$INPUT_CPPCHECK_ARGS" --output-file=cppcheck.txt -i"$GITHUB_WORKSPACE/$INPUT_EXCLUDE_DIR"
    run-clang-tidy-12 "^((?!$GITHUB_WORKSPACE/$INPUT_EXCLUDE_DIR).)*$" -- > clang_tidy.txt
fi

python3 /run_static_analysis.py -cc cppcheck.txt -ct clang_tidy.txt
