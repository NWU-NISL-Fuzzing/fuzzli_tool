import json
import logging
import pathlib
import random
import subprocess
import tempfile

import Result
from Reducer import simplifyTestcaseCore


def simplify_with_lithium(result: Result.HarnessResult):

    testcase = result.testcase.strip()
    [suspicious_outputs, normal_outputs] = simplifyTestcaseCore.split_output(result)
    if len(suspicious_outputs) == 0 or len(normal_outputs) == 0:
        return testcase
    candidate = [random.choice(suspicious_outputs), random.choice(normal_outputs)]
    try:
        with tempfile.NamedTemporaryFile(prefix="javascriptTestcase_", suffix=".js", delete=True) as f:
            testcase_path = pathlib.Path(f.name)
            
            candidate_simplified_testcase = None
            for output in candidate:
                testcase_path.write_bytes(bytes(testcase, encoding="utf-8"))
                simplify_core(output, testcase_path)
                simplified_testcase = testcase_path.read_text()
                
                if candidate_simplified_testcase is None:
                    candidate_simplified_testcase = simplified_testcase
                if simplified_testcase != testcase and \
                        simplifyTestcaseCore.check_effective(simplified_testcase, result)[0]:  
                    candidate_simplified_testcase = simplified_testcase
                    break
    except BaseException as e:
        logging.warning(e)
        return testcase
    return candidate_simplified_testcase if candidate_simplified_testcase is not None else testcase


def simplify_core(output: Result.Output, testcase_path: pathlib.Path):

    
    key_outputs = simplifyTestcaseCore.get_key_outputs(output).strip()
    key_outputs = json.dumps(key_outputs, ensure_ascii=True)
    command = f"/root/anaconda3/bin/python -m lithium outputs {key_outputs} " \
              f"{output.testbed} {str(testcase_path)}"
    print(command)
    pro = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, universal_newlines=True, shell=True)
    stdout, stderr =pro.communicate()
    
    
