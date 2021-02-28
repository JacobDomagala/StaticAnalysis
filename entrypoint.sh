#!/bin/bash

cd "$GITHUB_WORKSPACE"

export CXX=gcc-9

mkdir build && cd build
cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ..

cppcheck src --enable=all --suppress=missingInclude --inline-suppr --inconclusive --output-file=cppcheck.txt --project=compile_commands.json -i$GITHUB_WORKSPACE/dependencies
run-clang-tidy '^((?!/github/workspace/dependencies/).)*$' >(tee "output.txt")

# cat cppcheck.txt
# cat clang_tidy.txt

python3 /run_static_analysis.py -cc cppcheck.txt -ct clang_tidy.txt
