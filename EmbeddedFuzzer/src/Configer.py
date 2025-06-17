import json
import sqlite3

from Harness import *
from Mutator.mutation import Mutator
from Mutator.mutation import Mutator_arrayAndvar
from Mutator.mutation import Mutator_regex
from Postprocessor.callable_processor import CallableProcessor
from Reducer.Reduce import Reducer
from ResultFilter.classify import Classifier
from ResultFilter.errorinfo_classifier.errorinfo_db_operation import DataBase
from db import db_operation
from utils import getApisFromTestcase
from utils.parseTestbed import TestbedParser
from utils.uniformVariableName import Uniform


class Config:
    def __init__(self, config_path: str):
        
        
        self.config_path = str(pathlib.Path(config_path).absolute().resolve())
        self.config_check()
        with open(config_path, "r") as f:
            config = json.load(f)
        self.config = config
        self.workspace = pathlib.Path(config["workspace"])
        db_path = pathlib.Path(config["db_path"])
        self.error_info = self.workspace / "exception-info"
        self.api_instance = getApisFromTestcase.ESAPI(config["ESApis"])
        self.database = db_operation.DBOperation(str(db_path))
        self.harness = Harness(config["testbeds"], config["harness"]["mode"], config["harness"]["processes_num"])
        self.testbed_parser = TestbedParser(config["testbeds"])
        self.classify_db = DataBase(config["classify_db"])
        self.classifier = Classifier(self.api_instance, self.testbed_parser, self.classify_db)
        self.mutator = Mutator("node")
        self.mutator_arrayAndvar = Mutator_arrayAndvar("node")
        self.mutator_regex = Mutator_regex("node")
        self.reducer = Reducer()
        self.uniform = Uniform()

        self.error_info.mkdir(parents=True, exist_ok=True)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self.simples = None
        self.callable_processor = None
        

    def init_data(self):
        logging.info("Loading simples...")
        
        self.simples = self.database.query_corpus()
        
        self.callable_processor = CallableProcessor(self.simples)

    def config_check(self):
        if not pathlib.Path(self.config_path).exists():
            raise FileNotFoundError(f"Config file not exist: {self.config_path}")
        with open(self.config_path, "r") as f:
            config = json.load(f)
        simple_db = pathlib.Path(config["db_path"]).absolute().resolve()
        if not simple_db.is_file() or not simple_db.exists():
            conn = sqlite3.connect(simple_db)
            # raise FileNotFoundError(f"Corpus db file not exist: {simple_db}")
        
        classify_db = pathlib.Path(config["classify_db"])
        

        
        engines = config["testbeds"]
        self.engines_check(engines)

    def engines_check(self, testbeds: List[str]) -> bool:
        """
        check all engines is available
        :return:
            if all engines is available return ture, otherwise raise exception.
        :raise
            raise exception if any engine is not available.
        """
        if len(testbeds) == 0:
            raise Exception("No engine available, please check the configuration file.")
        with tempfile.NamedTemporaryFile(prefix="JavaScriptTestcase_", suffix=".js", delete=True) as f:
            p = pathlib.Path(f.name)
            p.write_text("var a = 1;\nprint(a);")

            for bed in testbeds:
                result = run_test_case(bed, p)
                if not result.returncode == 0:
                    logging.error(f"Enigine ERROR: {bed}\n"
                                  f"returncode = {str(result.returncode)}")
                    raise LookupError(f"Enigine ERROR: {bed}\n")
                
                elif result.stdout != "1\n":
                    raise Exception(f"Engine cannot be tested:\n {bed}. \n"
                                    f"When run the test case bellow, whose output should be \"1\\n\", but it's output is: \n"
                                    f"{result.stdout}")

    def close_resources(self):  
        self.database.close()


    
    
    def get_tested_count(self) -> int:
        return self.database.query_tested_count()
