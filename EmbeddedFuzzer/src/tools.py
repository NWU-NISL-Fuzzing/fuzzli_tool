import json
import pathlib
import sys

import Harness
import Result
from Reducer.Reduce import Reducer
from Result import HarnessResult
from db import db_operation
from utils.parseTestbed import TestbedParser

sys.path.extend(['../EmbeddedFuzzer', '../EmbeddedFuzzer/resources', '../EmbeddedFuzzer/src'])

config_path = '../EmbeddedFuzzer/resources/config-analysis.json'
testbed_parser = None


def get_output(harness_result: HarnessResult, mark: str = "*****") -> str:
    bug_type = [info.bug_type for info in Result.differential_test(original_harness_result)]
    output_id = set([info.output_id for info in Result.differential_test(original_harness_result)])
    bug_engines = [testbed_parser.get_engine_name(output.testbed)
                   for output in harness_result.outputs if output_id.__contains__(output.id)]

    output = str(bug_type) + "\n" + str(bug_engines) + "\n"
    for out in harness_result.outputs:
        output += f"{mark}{testbed_parser.get_engine_version(out.testbed)}{mark}".ljust(40, "*")
        output += f" [returncode: {out.returncode}] [duration: {out.duration_ms} ms]\n"
        output += f"{out.stdout}{out.stderr}\n"
    return output


def is_duplicate(case: str):
    for e in case.split("\n"):
        if e.find("dens_prev[i] = u_prev[i] = v_prev[i] = dens[i] = u[i] = v[i] = 0;") > -1:
            return True
    return False


if __name__ == '__main__':

    if {"-h", "--help"}.__contains__(sys.argv[1]):
        print("--commit: set the status of the test case to be manually checked\n" +
              "eg. python ../EmbeddedFuzzer/src/tools.py --commit test_case_id\n\n" +
              "--run: run test case and print harness result\n" +
              "eg. python ../EmbeddedFuzzer/src/tools.py --run testcase.js\n\n" +
              "--reduce: reduce test case and rewrite to file, besides print the harness result of reduced test case.\n" +
              "eg. python ../EmbeddedFuzzer/src/tools.py --reduce testcase.js\n\n" +
              "--get-testcase: get test case in ord or get test case with test case ID. Rewrite test case and id into "
              "file.\n" +
              "eg. python ../EmbeddedFuzzer/src/tools.py --get-testcase testcase.json [testcase_id]\n\n"
              )
        sys.exit()

    config_path = str(pathlib.Path(config_path).absolute().resolve())
    with open(config_path, "r") as f:
        config = json.load(f)
    harness = Harness.Harness(config["testbeds"], config["harness"]["mode"], config["harness"]["processes_num"])
    testbed_parser = TestbedParser(config["testbeds"])
    test_case_path = pathlib.Path(sys.argv[2])

    if sys.argv[1] == "--get-testcase":
        test_case_path.parent.mkdir(parents=True, exist_ok=True)
        database = db_operation.DBOperation(str(config["db_path"]))
        case_dict = {"id": -1, "testcase": "No related use cases found"}
        if len(sys.argv) == 4:  
            test_case_id = int(sys.argv[3])
            [case_dict["id"], case_dict["testcase"]] = database.query_mutated_test_case(test_case_id=test_case_id)[0]

        elif len(sys.argv) == 3:  
            [case_dict["id"], case_dict["testcase"]] = database.query_mutated_test_case_randomly()[0]
        while is_duplicate(case_dict["testcase"]):
            database.update_test_case_manual_checked_state(case_dict["id"])
            [case_dict["id"], case_dict["testcase"]] = database.query_mutated_test_case_randomly()[0]
        serialization = json.dumps(case_dict, indent=4)
        print(case_dict["testcase"])
        test_case_path.write_text(serialization)
        sys.exit()

    if sys.argv[1] == "--get-case":
        test_case_path.parent.mkdir(parents=True, exist_ok=True)
        database = db_operation.DBOperation(str(config["db_path"]))
        case_dict = {"id": -1, "testcase": "No related use cases found"}
        if len(sys.argv) == 4:  
            test_case_id = int(sys.argv[3])
            [case_dict["id"], case_dict["testcase"]] = database.query_mutated_test_case(test_case_id=test_case_id)[0]
        else:
            [case_dict["id"], case_dict["testcase"]] = database.query_mutated_test_case_randomly()[0]
        test_case_path.write_text(case_dict["testcase"])
        print(f"""testcase: {case_dict["testcase"]}""")
        print(f"""\n\nid: {case_dict["id"]}""")
        sys.exit()

    
    elif sys.argv[1] == "--commit":
        try:
            test_case_id = int(sys.argv[2])
            database = db_operation.DBOperation(str(config["db_path"]))
            database.update_test_case_manual_checked_state(test_case_id)
        except BaseException as e:
            print(e)
        else:
            print("Submitted successfully!")
        sys.exit()

    if not test_case_path.exists():
        print("File path note exist")
        sys.exit()
    test_case = test_case_path.read_text()
    original_harness_result = harness.run_testcase(test_case)

    if sys.argv[1] == "--run":
        print(get_output(original_harness_result))
    elif sys.argv[1] == "--reduce":
        reducer = Reducer()
        simplified_test_case = reducer.reduce(harness_result=original_harness_result)
        test_case_path.write_text(simplified_test_case)  
        
        print(get_output(harness.run_testcase(simplified_test_case)))

    else:
        print("Parameter passing error")
