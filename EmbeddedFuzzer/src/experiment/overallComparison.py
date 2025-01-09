import logging
import pathlib
import sys

import Result
from Configer import Config
from ResultFilter.classify import Classifier
from ResultFilter.errorinfo_classifier.errorinfo_db_operation import DataBase
from tqdm import tqdm

sys.path.extend(['../EmbeddedFuzzer', '../EmbeddedFuzzer/src'])
logging.basicConfig(level=logging.INFO,
                    format='%(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')


class Comparision:
    def __init__(self):
        config_path = "./resources/config-experiment.json"
        self.test_case_dirs = [
            "../codeCoverage/DIE/DIE_corpus",
            "../codeCoverage/codeAlchemist/codeAlchemist_corpus",
            "../codeCoverage/fuzzilli/fuzzilli_corpus",
            "../codeCoverage/montage/montage_corpus",
            "../codeCoverage/deepsmith/deepsmith_corpus"
        ]
        self.config = Config(config_path)

    def main(self):
        try:
            self.run()
        except BaseException as e:
            raise e
        finally:
            self.config.close_resources()

    def run(self):
        for case_dir in self.test_case_dirs:
            print(case_dir)
            tools_name = case_dir.split("/")[-2]
            self.config.classify_db = DataBase(f"mysql://root:nisl@10.15.10.113:3306/experiment{tools_name}?charset=utf8")
            self.config.classifier = Classifier(self.config.api_instance, self.config.testbed_parser, self.config.classify_db)
            result_dir = self.config.workspace / tools_name
            test_case_path_list = pathlib.Path(case_dir).rglob("*.js")
            test_case_path_list = list(test_case_path_list)
            test_case_path_list.sort()
            test_case_path_list = list(test_case_path_list)[:10000]
            print(f"test case total number is: {len(list(test_case_path_list))}")
            bug_counter = 0
            for test_case_path in tqdm(test_case_path_list):
                testcase = test_case_path.read_text()
                harness_result = self.config.harness.run_testcase(testcase)
                differential_test_result = Result.differential_test(harness_result)
                if len(differential_test_result) == 0:
                    continue
                classify_id_list = []
                for info in differential_test_result:
                    bug_counter += 1
                    [classify_result, classify_id] = self.config.classifier.is_suspicious_result(info.output_id,
                                                                                                 harness_result)
                    info.classify_result = classify_result.value
                    info.classify_id = classify_id
                    classify_id_list.append(classify_id)
                classify_id_list.sort()
                classification_file = "filtered-result-" + "-".join([str(e) for e in classify_id_list])
                (result_dir / classification_file).mkdir(parents=True, exist_ok=True)
                result_path = result_dir / classification_file / (str(test_case_path).split("/"))[-1]
                result_path.write_text(testcase)
                pathlib.Path(str(result_path) + "on").write_text(str(harness_result))
                
            print(f"\n{'=' * 20} Bug Number: {bug_counter}{'=' * 20} ")


if __name__ == '__main__':
    try:
        Comparision().main()
    except RuntimeError:
        sys.exit(1)