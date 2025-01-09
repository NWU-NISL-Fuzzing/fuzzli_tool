import json
import logging
import pathlib
import sys

from Configer import Config
from Reducer.reduce_with_lithium import simplify_with_lithium
from tqdm import tqdm
from utils import labdate

sys.path.extend(['../EmbeddedFuzzer', '../EmbeddedFuzzer/resources', '../EmbeddedFuzzer/src'])
logging.basicConfig(level=logging.INFO,
                    format='%(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')


class Fuzzer:
    def __init__(self):
        config_path = "./resources/config.json"
        self.config = Config(config_path)
        

    def main(self):
        try:
            self.run()
        except BaseException as e:
            raise e
        finally:
            self.config.close_resources()

    def run(self):
        
        self.lithium_evaluate()

    def lithium(self):
        testcase_list = json.loads(pathlib.Path("./test/data/lithium_testcase.json").read_text())
        simplified_reuslt_path = pathlib.Path("./test/data/lithium_simplified_testcase.json")
        original2simplified = []
        for testcase in tqdm(testcase_list):
            print("\n")
            harness_result = self.config.harness.run_testcase(testcase)
            simplify_start_time = labdate.GetUtcMillisecondsNow()
            simplified_testcase = simplify_with_lithium(harness_result)
            simplify_end_time = labdate.GetUtcMillisecondsNow()
            simplify_duration_ms = labdate.Datetime2Ms(simplify_end_time - simplify_start_time)
            original2simplified.append({"original": testcase, "simplified": simplified_testcase, "duration": simplify_duration_ms})
            simplified_reuslt_path.write_text(json.dumps(original2simplified, indent=4))

    def lithium_evaluate(self):
        simplified_reuslt_path = pathlib.Path("./test/data/lithium_simplified_testcase.json")
        simplified_reuslt = json.loads(simplified_reuslt_path.read_text())
        total_duration = 0
        total_original_line = 0
        total_simplified_line = 0
        testcase_size = len(simplified_reuslt)
        for ele in simplified_reuslt:
            total_original_line += len(ele["original"].strip().split("\n"))
            total_simplified_line += len(ele["simplified"].strip().split("\n"))
            total_duration += ele["duration"]
        print(f"\n{'=' * 20}lithium{'=' * 20}")
        print(f"Test case Counter: {testcase_size}")
        print(f"Averaged Simplify Duration: {total_duration / testcase_size} ms")
        print(f"Original Averaged  Lines: {total_original_line / testcase_size} ")
        print(f"Remained Averaged Lines: {total_simplified_line / testcase_size} ")
        print(f"Deleted Averaged Lines: {(total_original_line - total_simplified_line) / total_original_line}")


if __name__ == '__main__':
    try:
        Fuzzer().main()
    except RuntimeError:
        sys.exit(1)