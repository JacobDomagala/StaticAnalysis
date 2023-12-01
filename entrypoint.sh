#!/bin/bash

set -e

export TERM=xterm-color

debug_print() {
    if [ "$INPUT_VERBOSE" = "true" ]; then
        echo -e "\u001b[32m $1 \u001b[0m"
    fi
}

if [ "${INPUT_LANGUAGE,,}" = "c++" ]; then
    debug_print "Running checks on c++ code"
    source "./entrypoint_cpp.sh"
else
   debug_print "Running checks on Python code"
fi
