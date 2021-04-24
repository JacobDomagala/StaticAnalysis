#!/bin/bash

set -x

if [ -n "$INPUT_APT_PCKGS" ]; then
    for i in ${INPUT_APT_PCKGS//,/ }
    do
        apt-get update
        apt-get install -y "$i"
    done
fi

if [ -n "$INPUT_INIT_SCRIPT" ]; then
    chmod +x "$INPUT_INIT_SCRIPT"
    bash $INPUT_INIT_SCRIPT
fi

mkdir build && cd build || exit
cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ..

if [ -z "$INPUT_EXCLUDE_DIR" ]; then
    cppcheck src "$INPUT_CPPCHECK_ARGS" --output-file=cppcheck.txt --project=compile_commands.json
    run-clang-tidy >(tee "clang_tidy.txt")
else
    cppcheck src "$INPUT_CPPCHECK_ARGS" --output-file=cppcheck.txt --project=compile_commands.json -i"$GITHUB_WORKSPACE/$INPUT_EXCLUDE_DIR"
    run-clang-tidy "^((?!$GITHUB_WORKSPACE/$INPUT_EXCLUDE_DIR).)*$" > clang_tidy.txt
fi

python3 /run_static_analysis.py -cc cppcheck.txt -ct clang_tidy.txt
