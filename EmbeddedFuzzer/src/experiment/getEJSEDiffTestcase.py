import logging
import pathlib
import sys

from Configer import Config

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
        sql = "select id, testcase from OriginalTestcases order by RANDOM() limit 20000"
        testcase_list = self.config.database.query_template(sql=sql)
        testcase_dir = pathlib.Path("../codeCoverage/EJSEDiff/EJSEDiff_corpus_random_testcase_id")
        testcase_dir.mkdir(parents=True, exist_ok=True)
        for id, testcase in testcase_list:
            (testcase_dir / f"{id}.js").write_text(testcase)
        print(len(testcase_list))


if __name__ == '__main__':
    try:
        Comparision().main()
    except RuntimeError:
        sys.exit(1)