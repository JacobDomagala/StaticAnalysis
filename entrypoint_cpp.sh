#!/bin/bash
# shellcheck disable=SC2155

set -e

# Following variables are declared/defined in parent script
preselected_files=${preselected_files:-""}
print_to_console=${print_to_console:-false}
use_extra_directory=${use_extra_directory:-false}
common_ancestor=${common_ancestor:-""}

CLANG_TIDY_ARGS="${INPUT_CLANG_TIDY_ARGS//$'\n'/}"
CPPCHECK_ARGS="${INPUT_CPPCHECK_ARGS//$'\n'/}"

cd build

if [ "$INPUT_REPORT_PR_CHANGES_ONLY" = true ]; then
  if [ -z "$preselected_files" ]; then
        # Create empty files
        touch cppcheck.txt
        touch clang_tidy.txt

        cd /
        python3 -m src.static_analysis_cpp -cc "${GITHUB_WORKSPACE}/build/cppcheck.txt" -ct "${GITHUB_WORKSPACE}/build/clang_tidy.txt" -o "$print_to_console" -fk "$use_extra_directory" --common "$common_ancestor" --head "origin/$GITHUB_HEAD_REF"
        exit 0
   fi
fi

if [ "$INPUT_USE_CMAKE" = true ]; then
    # Trim trailing newlines
    INPUT_CMAKE_ARGS="${INPUT_CMAKE_ARGS%"${INPUT_CMAKE_ARGS##*[![:space:]]}"}"
    debug_print "Running cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON $INPUT_CMAKE_ARGS -S $GITHUB_WORKSPACE -B $(pwd)"
    eval "cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON $INPUT_CMAKE_ARGS -S $GITHUB_WORKSPACE -B $(pwd)"
fi

if [ -z "$INPUT_EXCLUDE_DIR" ]; then
    files_to_check=$(python3 /src/get_files_to_check.py -dir="$GITHUB_WORKSPACE" -preselected="$preselected_files" -lang="c++")
    debug_print "Running: files_to_check=python3 /src/get_files_to_check.py -dir=\"$GITHUB_WORKSPACE\" -preselected=\"$preselected_files\" -lang=\"c++\")"
else
    files_to_check=$(python3 /src/get_files_to_check.py -exclude="$GITHUB_WORKSPACE/$INPUT_EXCLUDE_DIR" -dir="$GITHUB_WORKSPACE" -preselected="$preselected_files" -lang="c++")
    debug_print "Running: files_to_check=python3 /src/get_files_to_check.py -exclude=\"$GITHUB_WORKSPACE/$INPUT_EXCLUDE_DIR\" -dir=\"$GITHUB_WORKSPACE\" -preselected=\"$preselected_files\" -lang=\"c++\")"
fi

debug_print "Files to check = $files_to_check"
debug_print "CPPCHECK_ARGS = $CPPCHECK_ARGS"
debug_print "CLANG_TIDY_ARGS = $CLANG_TIDY_ARGS"

num_proc=$(nproc)

if [ -z "$files_to_check" ]; then
    echo "No files to check"
else
    if [ "$INPUT_USE_CMAKE" = true ]; then
        for file in $files_to_check; do
            exclude_arg=""
            if [ -n "$INPUT_EXCLUDE_DIR" ]; then
                exclude_arg="-i$GITHUB_WORKSPACE/$INPUT_EXCLUDE_DIR"
            fi

            # Replace '/' with '_'
            file_name=$(echo "$file" | tr '/' '_')

            debug_print "Running cppcheck --project=compile_commands.json $CPPCHECK_ARGS --file-filter=$file --output-file=cppcheck_$file_name.txt $exclude_arg"
            eval cppcheck --project=compile_commands.json "$CPPCHECK_ARGS" --file-filter="$file" --output-file="cppcheck_$file_name.txt" "$exclude_arg" || true
        done

        cat cppcheck_*.txt > cppcheck.txt

        # Excludes for clang-tidy are handled in python script
        debug_print "Running run-clang-tidy-20 $CLANG_TIDY_ARGS -p $(pwd) $files_to_check >>clang_tidy.txt 2>&1"
        eval run-clang-tidy-20 "$CLANG_TIDY_ARGS" -p "$(pwd)" "$files_to_check" >clang_tidy.txt 2>&1 || true

    else
        # Excludes for clang-tidy are handled in python script
        debug_print "Running cppcheck -j $num_proc $files_to_check $CPPCHECK_ARGS --output-file=cppcheck.txt ..."
        eval cppcheck -j "$num_proc" "$files_to_check" "$CPPCHECK_ARGS" --output-file=cppcheck.txt || true

        debug_print "Running run-clang-tidy-20 $CLANG_TIDY_ARGS $files_to_check >>clang_tidy.txt 2>&1"
        eval run-clang-tidy-20 "$CLANG_TIDY_ARGS" "$files_to_check" >clang_tidy.txt 2>&1 || true
    fi

    cd /

    python3 -m src.static_analysis_cpp -cc "${GITHUB_WORKSPACE}/build/cppcheck.txt" -ct "${GITHUB_WORKSPACE}/build/clang_tidy.txt" -o "$print_to_console" -fk "$use_extra_directory" --common "$common_ancestor" --head "origin/$GITHUB_HEAD_REF"
fi
