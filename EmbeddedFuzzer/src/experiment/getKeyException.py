import json
import logging
import pathlib
import sys

from Configer import Config
from ResultFilter.classify import *

sys.path.extend(['../EmbeddedFuzzer', '../EmbeddedFuzzer/src'])
logging.basicConfig(level=logging.INFO,
                    format='%(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')


class Comparision:
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
        self.get_key_exception()

    def query_deformity_result(self):
        sql = """select * from Outputs where returncode == 0 and stderr != ''"""
        query_result = self.config.database.query_template(sql)
        print(len(query_result))
        result_list = []
        for e in query_result:
            tmp = {
                "id": e[0],
                "testcase_id": e[1],
                "testbed_id": e[2],
                "returncode": e[3],
                "stdout": e[4],
                "stderr": e[5]
            }
            result_list.append(tmp)
        serialization = json.dumps(result_list, indent=4)
        print(serialization)
        pathlib.Path("./test/tmp/abnormal_output.json").write_text(serialization)

    def analyse_deformity_result(self):
        serialization = pathlib.Path("./test/tmp/abnormal_output.json").read_text()
        result_list = json.loads(serialization)
        testcase_id_set = set()
        testbed_set = set()
        for e in list(result_list):
            testcase_id_set.add(e["testcase_id"])
            testbed_set.add(e["testbed_id"])

        sql = """select testbed from Engines where id=?"""
        print(f"{'='*10}testbeds{'='*10}\n")
        for testbed_id in testbed_set:
            print(self.config.database.query_template(sql, [testbed_id])[0][0])

        testcase = []
        sql = """select testcase from Testcases where id=?"""
        for testcase_id in testcase_id_set:
            testcase.append(self.config.database.query_template(sql, [testcase_id])[0][0])
        print(f"{'='*10}testcase num: {len(testcase)}{'='*10}")
        pathlib.Path("./test/tmp/abnormal_testcase.txt").write_text(("=" * 30 + "\n").join(testcase))

    def get_key_exception(self):
        sql = """select * from Outputs where returncode > 0 """
        query_result = self.config.database.query_template(sql)
        print(f"Number of query： {len(query_result)}")
        key_exception_not_matched_list = []
        not_matched_stderr_list = []
        key_exception_list = []
        for e in query_result:
            stderr = e[5]
            key_exception = ""
            try:
                key_exception = list_normalized_essential_exception_message(stderr)
            except BaseException as e:
                breakpoint()
            if key_exception == "":  
                tmp = {
                    "id": e[0],
                    "testcase_id": e[1],
                    "testbed_id": e[2],
                    "returncode": e[3],
                    "stdout": e[4],
                    "stderr": e[5]
                }
                key_exception_not_matched_list.append(tmp)
                not_matched_stderr_list.append(stderr)
            else:  
                key_exception_list.append(key_exception)
        pathlib.Path("./test/tmp/not_matched_stderr.txt").write_text(("\n\n" + "=" * 50 + "\n\n").join(not_matched_stderr_list))
        pathlib.Path("./test/tmp/key_exception.txt").write_text(("\n\n" + "=" * 50 + "\n\n").join(key_exception_list))
        pathlib.Path("./test/tmp/key_exception_not_matched_list.txt").write_text(json.dumps(key_exception_not_matched_list, indent=4))

    def get_key_information(self):
        pass


if __name__ == '__main__':
    try:
        Comparision().main()
    except RuntimeError:
        sys.exit(1)
