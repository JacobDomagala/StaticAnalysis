#!/bin/bash
# shellcheck disable=SC1091

set -e

export TERM=xterm-color

debug_print() {
    if [ "$INPUT_VERBOSE" = "true" ]; then
        echo -e "\u001b[32m $1 \u001b[0m"
    fi
}

if [ "$RUNNER_DEBUG" = "1" ]; then
    export INPUT_VERBOSE="true"
    debug_print "Runner is running in debug mode - enabling verbose output"
fi

print_to_console=${INPUT_FORCE_CONSOLE_PRINT}
check_cpp=$( [ "${INPUT_LANGUAGE,,}" = "c++" ] && echo "true" || echo "false" )
check_python=$( [ "${INPUT_LANGUAGE,,}" = "python" ] && echo "true" || echo "false" )

# Some debug info
debug_print "Print to console = $print_to_console"

if [ "$print_to_console" = true ]; then
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
original_root_dir="$GITHUB_WORKSPACE"

# This is useful when running this Action from fork (together with [pull_request_target])
if [ "$GITHUB_EVENT_NAME" = "pull_request_target" ] && [ -n "$INPUT_PR_REPO" ]; then
    debug_print "Running in [pull_request_target] event! Cloning the Head repo ..."
    [ ! -d 'pr_tree' ] && git clone "https://www.github.com/$INPUT_PR_REPO" pr_tree
    cd pr_tree || exit
    git checkout "$INPUT_PR_HEAD"
    use_extra_directory=true

    # Override commit SHA, in order to get the correct code snippet
    NEW_GITHUB_SHA=$(git rev-parse HEAD)

    export GITHUB_SHA=$NEW_GITHUB_SHA
    pwd=$(pwd)
    export GITHUB_WORKSPACE=$pwd
fi

preselected_files=""
common_ancestor=""
if [ "$INPUT_REPORT_PR_CHANGES_ONLY" = true ]; then
    echo "The 'report_pr_changes_only' option is enabled. Running SA only on modified files."
    git config --global --add safe.directory /github/workspace
    git fetch origin
    common_ancestor=$(git merge-base origin/"$GITHUB_BASE_REF" "origin/$GITHUB_HEAD_REF")
    debug_print "Common ancestor: $common_ancestor"
    if [ "$check_cpp" = "true" ]; then
        preselected_files="$(git diff --name-only "$common_ancestor" "origin/$GITHUB_HEAD_REF" | grep -E '\.(c|cpp|h|hpp)$')" || true
        output_string="No (C/C++) files changed in the PR! Only files ending with .c, .cpp, .h, or .hpp are considered."
    fi

    if [ "$check_python" = "true" ]; then
        preselected_files="$(git diff --name-only "$common_ancestor" "origin/$GITHUB_HEAD_REF" | grep -E '\.(py)$')" || true
        output_string="No Python files changed in the PR! Only files ending with .py are considered."
    fi

    if [ -z "$preselected_files" ]; then
        debug_print "$output_string"
    else
        debug_print "Preselected files: \n$preselected_files"
    fi
fi

debug_print "GITHUB_WORKSPACE = ${GITHUB_WORKSPACE} INPUT_EXCLUDE_DIR = ${INPUT_EXCLUDE_DIR} use_extra_directory = ${use_extra_directory}"

mkdir -p build

if [ -n "$INPUT_INIT_SCRIPT" ]; then
    # Use $original_root_dir here, just in case we're running in pull_request_target
    chmod +x "$original_root_dir/$INPUT_INIT_SCRIPT"
    # shellcheck source=/dev/null
    source "$original_root_dir/$INPUT_INIT_SCRIPT" "$GITHUB_WORKSPACE" "$GITHUB_WORKSPACE/build"
fi

if [ "${INPUT_LANGUAGE,,}" = "c++" ]; then
    debug_print "Running checks on c++ code"
    source "/src/entrypoint_cpp.sh"
else # assume python
    debug_print "Running checks on Python code"
    source "/src/entrypoint_python.sh"
fi
