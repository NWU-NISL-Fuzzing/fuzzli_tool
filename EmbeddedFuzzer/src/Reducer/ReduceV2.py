import subprocess
import pathlib
import random
import os

import sys
sys.path.extend(['/home/fuzzli_tool/EmbeddedFuzzer', '/home/fuzzli_tool/EmbeddedFuzzer/resources', '/home/fuzzli_tool/EmbeddedFuzzer/src'])

from Configer import Config
from Reducer import simplifyTestcaseCore
from utils import labdate
from utils import JSASTOpt
import Result


config = Config("resources/config.json")
testbed_path = pathlib.Path("resources/testbed.sh")
testbed_content = testbed_path.read_text()
output_jsfile_path = "/home/reduce/data_v3/test.js"
output_shfile_path = "/home/reduce/data_v3/test.sh"

def read_simplified_result():
    if os.path.exists(output_jsfile_path):
        testcase_path = pathlib.Path(output_jsfile_path)
    else:
        return None
    simplified_testcase = testcase_path.read_text()
    return simplified_testcase


def use_vulcan():
    """ Run Vulcan. """

    command = "java -jar /home/reduce/perses_deploy.jar -t /home/reduce/test.sh --enable-vulcan true -i /home/reduce/test.js -o /home/reduce/data_v3"
    try:
        pro = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        stdout, stderr =pro.communicate(timeout=600)
        print(stdout)
        print(stderr)
    except subprocess.TimeoutExpired:
        print("The process timed out after 10 minutes.")
        pro.kill()  # Kill the process if it times out
        return None
    except:
        traceback.print_exc()
        return None
    return read_simplified_result()


def get_name_and_output(result):
    """ Get engine name and extract key information from stdout and stderr. """

    testbed = result.testbed
    if "mujs" in testbed:
        name = "mujs"
    elif "hermes" in testbed:
        name = "hermes"
    elif "quickjs" in testbed:
        name = "quickjs"
    elif "jerryscript" in testbed:
        name = "jerryscript"
    elif "moddable" in testbed:
        name = "xs"
    elif "duktape" in testbed:
        name = "duktape"
    output = simplifyTestcaseCore.get_key_outputs(result).strip()
    return name, output


def construct_interestingness_script(badcc_name, normal_outputs: list):
    """ Construct the customized interestingness test for one anomaly. """

    with open('resources/template.sh', 'r') as f:
        template = f.read()
    exec_stmt = {
        'mujs' : 'mujs_output=$( /home/engines/mujs/mujs-1.3.2/build/release/mujs "${test_file}" 2>&1 )',
        'hermes' : 'hermes_output=$( /home/engines/hermes/hermes-0.12.0/build_release/bin/hermes -w "${test_file}" 2>&1 )',
        'quickjs' : 'quickjs_output=$( /home/engines/quickjs/quickjs-2021-03-27/qjs "${test_file}" 2>&1 )',
        'jerryscript' : 'jerryscript_output=$( /home/engines/jerryscript/jerryscript-2.4.0/jerryscript-2.4.0/build/bin/jerry "${test_file}" 2>&1 )',
        'xs' : 'xs_output=$( /home/engines/XS/moddable-4.2.1/build/bin/lin/release/xst "${test_file}" 2>&1 )',
        'duktape' : 'duktape_output=$( /home/engines/duktape/duktape-2.7.0/duk "${test_file}" 2>&1 )'
    }
    # Choose one from suspicious_outputs(BADCC). Version origianl and ours need to be same.
    goodcc = random.choice(normal_outputs)
    goodcc1 = normal_outputs[0]
    goodcc_name1, goodcc_output1 = get_name_and_output(goodcc1)
    check_str = ""
    for goodcc2 in normal_outputs[1:]:
        goodcc_name2, goodcc_output2 = get_name_and_output(goodcc2)
        check_str += f'"${{{goodcc_name1}_output}}" == "${{{goodcc_name2}_output}}" && '
    check_str += f'"${{{goodcc_name1}_output}}" != "${{{badcc_name}_output}}" '
    script_content = f"""{testbed_content}
if [[ {check_str} ]]; then
    exit 0
else
    exit 1
fi
"""

    # Write down.
    shfile_path = '/home/reduce/test.sh'
    with open(shfile_path, "w") as f:
        f.write(template.replace("[REPLACE_HERE]", script_content))


def construct_and_reduce(suspicious_output, normal_outputs: list):
    """ Call construct_interestingness_script and active reduction tools (specified by `tool`). """

    construct_interestingness_script(get_name_and_output(suspicious_output), normal_outputs)
    simplify_start_time = labdate.GetUtcMillisecondsNow()
    simplified_testcase = use_vulcan()
    simplify_end_time = labdate.GetUtcMillisecondsNow()
    simplify_duration_ms = labdate.Datetime2Ms(simplify_end_time - simplify_start_time)
    if os.path.exists(output_jsfile_path):
        os.remove(output_jsfile_path)
    if os.path.exists(output_jsfile_path):
        os.remove(output_shfile_path)
    return simplified_testcase, simplify_duration_ms


class Reducer:
    def reduce(self, suspicious_output, normal_outputs) -> str:
        simplified_testcase, simplify_duration_ms = construct_and_reduce(suspicious_output, normal_outputs)
        if simplified_testcase is None or len(simplified_testcase) == 0:
            simplified_testcase = testcase
        return simplified_testcase

if __name__ == '__main__':
    reducer = Reducer()
    with open("/home/reduce/test.js", "r") as f:
        testcase = f.read()
    result = config.harness.run_testcase(testcase)
    [suspicious_outputs, normal_outputs] = simplifyTestcaseCore.split_output(result)
    simplified_testcase = reducer.reduce(suspicious_outputs[0], normal_outputs)
    print(simplified_testcase)
