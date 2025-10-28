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
RUN_CLANG_TIDY_BIN="${RUN_CLANG_TIDY_BIN:-$(command -v run-clang-tidy || command -v "run-clang-tidy-${CLANG_VERSION:-23}" || compgen -c | grep '^run-clang-tidy-[0-9]\+$' | head -n 1 || true)}"

if [ -z "$RUN_CLANG_TIDY_BIN" ]; then
    debug_print "Error: run-clang-tidy executable not found in PATH."
    exit 1
fi

if [ -n "$INPUT_COMPILE_COMMANDS" ]; then
    debug_print "Using compile_commands.json file ($INPUT_COMPILE_COMMANDS) - use_cmake input is not being used!"
    export INPUT_USE_CMAKE=false
    if [ "$INPUT_COMPILE_COMMANDS_REPLACE_PREFIX" = true ]; then
        debug_print "Replacing prefix inside user generated compile_commands.json file!"
        python3 /src/patch_compile_commands.py "/github/workspace/$INPUT_COMPILE_COMMANDS"
    fi
fi

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
    files_to_check=$(python3 /src/get_files_to_check.py -exclude="$INPUT_EXCLUDE_DIR" -dir="$GITHUB_WORKSPACE" -preselected="$preselected_files" -lang="c++")
    debug_print "Running: files_to_check=python3 /src/get_files_to_check.py -exclude=\"$INPUT_EXCLUDE_DIR\" -dir=\"$GITHUB_WORKSPACE\" -preselected=\"$preselected_files\" -lang=\"c++\")"
fi

debug_print "Files to check = $files_to_check"
debug_print "CPPCHECK_ARGS = $CPPCHECK_ARGS"
debug_print "CLANG_TIDY_ARGS = $CLANG_TIDY_ARGS"

cppcheck_exclude_args=""
if [ -n "$INPUT_EXCLUDE_DIR" ]; then
    read -r -a exclude_dirs <<< "$INPUT_EXCLUDE_DIR"
    for exclude_dir in "${exclude_dirs[@]}"; do
        exclude_path="$exclude_dir"
        if [[ "$exclude_path" != /* ]]; then
            exclude_path="$GITHUB_WORKSPACE/$exclude_path"
        fi
        cppcheck_exclude_args="$cppcheck_exclude_args -i$exclude_path"
    done
fi

num_proc=$(nproc)

if [ -z "$files_to_check" ]; then
    echo "No files to check"
else
    if [ "$INPUT_USE_CMAKE" = true ] || [ -n "$INPUT_COMPILE_COMMANDS" ]; then
        # Determine path to compile_commands.json
        if [ -n "$INPUT_COMPILE_COMMANDS" ]; then
            compile_commands_path="/github/workspace/$INPUT_COMPILE_COMMANDS"
            compile_commands_dir=$(dirname "$compile_commands_path")

        else
            compile_commands_path="compile_commands.json"
            compile_commands_dir=$(pwd)
        fi

        for file in $files_to_check; do
            # Replace '/' with '_'
            file_name=$(echo "$file" | tr '/' '_')

            debug_print "Running cppcheck --project=$compile_commands_path $CPPCHECK_ARGS --file-filter=$file --output-file=cppcheck_$file_name.txt $cppcheck_exclude_args"
            cppcheck_cmd="cppcheck --project=\"$compile_commands_path\" $CPPCHECK_ARGS --file-filter=\"$file\" --output-file=\"cppcheck_$file_name.txt\"$cppcheck_exclude_args"
            eval "$cppcheck_cmd" || true
        done

        cat cppcheck_*.txt > cppcheck.txt

        # Excludes for clang-tidy are handled in python script
        debug_print "Running $RUN_CLANG_TIDY_BIN $CLANG_TIDY_ARGS -p $compile_commands_dir $files_to_check >>clang_tidy.txt 2>&1"
        eval "$RUN_CLANG_TIDY_BIN" "$CLANG_TIDY_ARGS" -p "$compile_commands_dir" "$files_to_check" > clang_tidy.txt 2>&1 || true

    else
        # Without compile_commands.json
        debug_print "Running cppcheck -j $num_proc $files_to_check $CPPCHECK_ARGS --output-file=cppcheck.txt ..."
        eval cppcheck -j "$num_proc" "$files_to_check" "$CPPCHECK_ARGS" --output-file=cppcheck.txt || true

        debug_print "Running $RUN_CLANG_TIDY_BIN $CLANG_TIDY_ARGS $files_to_check >>clang_tidy.txt 2>&1"
        eval "$RUN_CLANG_TIDY_BIN" "$CLANG_TIDY_ARGS" "$files_to_check" > clang_tidy.txt 2>&1 || true
    fi

    cd /

    python3 -m src.static_analysis_cpp -cc "${GITHUB_WORKSPACE}/build/cppcheck.txt" -ct "${GITHUB_WORKSPACE}/build/clang_tidy.txt" -o "$print_to_console" -fk "$use_extra_directory" --common "$common_ancestor" --head "origin/$GITHUB_HEAD_REF"
fi
