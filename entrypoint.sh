#!/bin/bash

set -x

if [ -n "$INPUT_APT_PCKGS" ]; then
    for i in ${INPUT_APT_PCKGS//,/ }
    do
        apt-get install -y "$i"
    done
fi

cd "$GITHUB_WORKSPACE" || exit

mkdir build && cd build || exit
cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ..

if [ -z "$INPUT_EXCLUDE_DIR" ]; then
    cppcheck src --enable=all --suppress=missingInclude --inline-suppr --inconclusive --output-file=cppcheck.txt --project=compile_commands.json
    run-clang-tidy >(tee "clang_tidy.txt")
else
    cppcheck src --enable=all --suppress=missingInclude --inline-suppr --inconclusive --output-file=cppcheck.txt --project=compile_commands.json -i"$GITHUB_WORKSPACE/$INPUT_EXCLUDE_DIR"
    run-clang-tidy "^((?!$GITHUB_WORKSPACE/$INPUT_EXCLUDE_DIR).)*$" > clang_tidy.txt
fi

python3 /run_static_analysis.py -cc cppcheck.txt -ct clang_tidy.txt
