import logging
import sys
import os

from tqdm import tqdm

sys.path.extend(['../EmbeddedFuzzer', '../EmbeddedFuzzer/src'])
from Configer import Config
import Result
from utils import crypto

import random

logging.basicConfig(level=logging.INFO,
                    format='%(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')


class Fuzzer:
    def __init__(self):
        config_path = "./resources/config.json"
        self.config = Config(config_path)
        self.config.init_data()

    def main(self):
        try:
            self.run()
        except BaseException as e:
            raise e
        finally:
            self.config.close_resources()

    def find_js_files(self, folder):
        js_files = []
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith('.js'):  
                    js_files.append(os.path.join(root, file))
        return js_files

    def run(self):
        
        
        folder_path = '../../after/compares/generateCorpus'
        js_files = self.find_js_files(folder_path)
        a=0
        for file in js_files:
            print(a)
            a=a+1
            with open(file, 'r') as file1:
                case = file1.read()
                self.config.database.insert_corpus1(case)
        
        
    def uniform(self, test_case: str) -> str:
        try:
            uniformed_test_case = self.config.uniform.uniform_variable_name(test_case)
            original_harness_result = self.config.harness.run_testcase(test_case)
            uniformed_harness_result = self.config.harness.run_testcase(uniformed_test_case)
            
            if len(Result.differential_test(original_harness_result)) == len(Result.differential_test(
                    uniformed_harness_result)):
                return uniformed_test_case
        except BaseException as e:
            pass
        return test_case

    def save_interesting_test_case(self, test_case: str):
        hash_code = crypto.md5_str(test_case)
        file_path = (self.config.workspace / f"interesting_testcase/{hash_code}.js").absolute().resolve()  
        file_path.parent.mkdir(parents=True, exist_ok=True)  
        logging.info(f"\nInteresting test case is writen to the file:\n {file_path}")
        file_path.write_text(test_case)  


if __name__ == '__main__':
    try:
        Fuzzer().main()
    except RuntimeError:
        sys.exit(1)
