import logging
import pathlib
import sys

from Configer import Config

sys.path.extend(['../EmbeddedFuzzer', '../EmbeddedFuzzer/resources', '../EmbeddedFuzzer/src'])
logging.basicConfig(level=logging.INFO,
                    format='%(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')


class Fuzzer:
    def __init__(self):
        config_path = "./resources/config.json"
        self.config = Config(config_path)
        
        self.harness_dirs = [
            "../workspace/experiment/DIE",
            "../workspace/experiment/codeAlchemist",
            "../workspace/experiment/fuzzilli",
            "../workspace/experiment/montage",
            "../workspace/experiment/deepsmith"
        ]

    def main(self):
        try:
            self.run()
        except BaseException as e:
            raise e
        finally:
            self.config.close_resources()

    def run(self):
        pass

    def counter_bug_sum(self):
        for case_dir in self.harness_dirs:
            bug_counter = 0
            for child_dir in pathlib.Path(case_dir).iterdir():
                t = str(child_dir).split("-")
                if len(t) < 3:
                    continue
                classify_id_list = [int(e) for e in t[2:]]
                js_path_list = list(child_dir.rglob("*.js"))
                bug_counter += len(js_path_list) * len(classify_id_list)
            print(case_dir.split("/")[-1] + " bug numbers:" + str(bug_counter))





if __name__ == '__main__':
    try:
        Fuzzer().main()
    except RuntimeError:
        sys.exit(1)
