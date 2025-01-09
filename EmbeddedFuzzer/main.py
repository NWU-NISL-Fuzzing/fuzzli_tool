import logging
import sys

from tqdm import tqdm
from typing import List
sys.path.extend(['../EmbeddedFuzzer', '../EmbeddedFuzzer/src'])
from Configer import Config
import Result
from utils import crypto

import random

logging.basicConfig(level=logging.INFO,
                    format='%(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')

LOOP_MUTATOR = True
ARRAY_MUTATOR = True
REGEX_MUTATOR = True
STRING_MUTATOR = True
OBJECT_MUTATOR = True

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

    def run(self):
        
        for simple in tqdm(self.config.simples, ncols=100):
            original_test_case = self.config.callable_processor.get_self_calling(simple)

            print("")
            original_test_case_id = self.config.database.insert_original_testcase(testcase=original_test_case,
                                                                                  simple=simple)
            if self.premutation(original_test_case):
                self.config.database.update_simple_status(simple)
                continue

            flag = self.config.database.query_flag(original_test_case_id)
            print(original_test_case_id)
            flag = int(flag, 2)
            mutated_test_case_list=self.mutationByFlag(flag, original_test_case)

            for mutated_test_case in mutated_test_case_list:
                harness_result = self.config.harness.run_testcase(mutated_test_case)
                
                [harness_result, test_case_id] = self.config.database.insert_harness_result(harness_result,
                                                                                            original_test_case_id)
                differential_test_result = Result.differential_test(harness_result)
                if len(differential_test_result) == 0:
                    continue
                simplified_test_case = self.config.reducer.reduce(harness_result)
                
                uniformed_test_case = self.uniform(simplified_test_case)
                new_harness_result = self.config.harness.run_testcase(uniformed_test_case)
                
                '''
                suspicious_differential_test_result_list = self.config.classifier.filter(
                    Result.differential_test(new_harness_result), new_harness_result)
                self.config.database.insert_differential_test_results(suspicious_differential_test_result_list)
                if len(suspicious_differential_test_result_list) == 0:  
                    continue
                '''
                
                new_differential_test_result = Result.differential_test(new_harness_result)
                if len(new_differential_test_result) == 0:
                    continue
                self.config.database.insert_differential_test_results(new_differential_test_result, mutated_test_case)
                
                self.save_interesting_test_case(uniformed_test_case)
            self.config.database.update_simple_status(simple)  

    
    def premutation(self, original_test_case: str) -> bool:
        harness_result = self.config.harness.run_testcase(original_test_case)
        for output in harness_result.outputs:
            stderr = output.stderr
            
            if stderr is None:
                return False
            if "TypeError" not in stderr:
                return False
        return True

    
    def mutation(self, original_test_case: str) -> List[str]:
        mutated_test_case_list = []
        
        mutated_test_case_list.extend(self.config.mutator.mutate(original_test_case, max_size=20))
        
        rand_num = random.randint(0, 99)
        if rand_num < 5:
            
            temp = self.config.mutator_arrayAndvar.mutate_longArrMethod(original_test_case, max_size=1)
            if temp is not None:
                mutated_test_case_list.extend(temp)
        rand_num1 = random.randint(0, 99)
        if rand_num1 < 5:
            
            temp = self.config.mutator_arrayAndvar.mutate_typearr(original_test_case, max_size=1)
            if temp is not None:
                mutated_test_case_list.extend(temp)
        rand_num2 = random.randint(0, 99)
        if rand_num2 < 5:
            
            mutated_test_case_list.extend(self.config.mutator_regex.mutate_regEx(original_test_case, max_size=1))
        mutated_test_case_list.append(original_test_case)
        return mutated_test_case_list

    
    def mutationByFlag(self, flag: int, original_test_case: str) -> List[str]:
        
        mutated_test_case_list = []
        
        if LOOP_MUTATOR and (flag & 0b10000 ==0b10000):
            differ=self.getTime(original_test_case)
            if differ > 30:
                mutated_test_case_list.extend(self.config.mutator.mutate(original_test_case, max_size=20))
        
        if ARRAY_MUTATOR and (flag & 0b01000 ==0b01000):
            mutated_test_case_list.extend(self.config.mutator.mutateByArray(original_test_case, max_size=1))
        
        if REGEX_MUTATOR and (flag & 0b00100 ==0b00100):
            mutated_test_case_list.extend(self.config.mutator.mutateByRegex(original_test_case, max_size=1))
        
        if STRING_MUTATOR and (flag & 0b00010 ==0b00010):
            mutated_test_case_list.extend(self.config.mutator.mutateByString(original_test_case, max_size=1))
        
        if OBJECT_MUTATOR and (flag & 0b00001 ==0b00001):
            mutated_test_case_list.extend(self.config.mutator.mutateByObject(original_test_case, max_size=1))
        mutated_test_case_list.append(original_test_case)
        return mutated_test_case_list

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

   
    def getTime(self, originalTestcase:str) -> int:
        harness_result = self.config.harness.run_testcase(originalTestcase)
        min_duration = min([output.duration_ms for output in harness_result.outputs])
        max_duration = max([output.duration_ms for output in harness_result.outputs])
        differ=max_duration-min_duration
        return differ



if __name__ == '__main__':
    try:
       
        Fuzzer().main()
    except RuntimeError:
        sys.exit(1)
