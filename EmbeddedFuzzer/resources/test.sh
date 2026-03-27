#!/bin/bash
set -o pipefail
set -o nounset
ulimit -t 60

test_file="test.js"

mujs_output=$( /home/fuzzli_tool/engines/mujs/mujs-1.3.2/build/release/mujs "${test_file}" 2>&1 )
hermes_output=$( /home/fuzzli_tool/engines/hermes/hermes-0.12.0/build_release/bin/hermes -w "${test_file}" 2>&1 )
quickjs_output=$( /home/fuzzli_tool/engines/quickjs/quickjs-2021-03-27/qjs "${test_file}" 2>&1 )
jerryscript_output=$( /home/fuzzli_tool/engines/jerryscript/jerryscript-2.4.0/jerryscript-2.4.0/build/bin/jerry "${test_file}" 2>&1 )
xs_output=$( /home/fuzzli_tool/engines/XS/moddable-4.2.1/build/bin/lin/release/xst "${test_file}" 2>&1 )
duktape_output=$( /home/fuzzli_tool/engines/duktape/duktape-2.7.0/duk "${test_file}" 2>&1 )

if [[ "${hermes_output}" == "${quickjs_output}" && "${hermes_output}" == "${xs_output}" && "${hermes_output}" != "${('duktape', 'SyntaxError: parse error (line 5)')_output}"  ]]; then
    exit 0
else
    exit 1
fi

