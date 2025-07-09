import random
import logging
import argparse
from tqdm import tqdm
from typing import List
from termcolor import cprint

import sys
sys.path.extend(['../EmbeddedFuzzer', '../EmbeddedFuzzer/src'])

from utils import crypto
from Configer import Config
import Result

logging.basicConfig(level=logging.INFO,
                    format='%(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
parser = argparse.ArgumentParser()
parser.add_argument('--step', type=int, default=1, help='step0.run all steps\nstep1.mutate\nstep2.differential testing\n3.reduce')
parser.add_argument('--size', type=int, default=10, help='the number of test cases')
args = parser.parse_args()

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
            step = args.step
            size = args.size
            if step == 0:
                self.step0(size)
            elif step == 1:
                self.step1(size)
            elif step == 2:
                self.step2(size)
            elif step == 3:
                self.step3(size)
            cprint("Fuzzing finished.", "blue")
        except BaseException as e:
            raise e
        finally:
            self.config.close_resources()

    def step0(self, size: int):
        # for sample in tqdm(self.config.samples, ncols=100):
        if size > len(self.config.samples):
            size = len(self.config.samples)
        for i in range(size):
            sample = self.config.samples[i]
            # Step1. Obtain seed program and mutate.
            original_test_case = self.config.callable_processor.get_self_calling(sample)
            original_test_case_id = self.config.database.insert_original_testcase(testcase=original_test_case, sample=sample)
            self.config.database.commit()
            if self.premutation(original_test_case):
                self.config.database.update_sample_status(sample)
                continue
            flag = self.config.database.query_flag(original_test_case_id)
            print(original_test_case_id)
            flag = int(flag, 2)
            mutated_test_case_list=self.mutationByFlag(flag, original_test_case)
            # Step2. Differential testing.
            for mutated_test_case in mutated_test_case_list:
                harness_result = self.config.harness.run_testcase(mutated_test_case)
                [harness_result, test_case_id] = self.config.database.insert_harness_result(harness_result,
                                                                                            original_test_case_id)
                differential_test_result = Result.differential_test(harness_result)
                if len(differential_test_result) == 0:
                    continue
                # Step3. Reduce.
                # simplified_test_case = self.config.reducer.reduce(harness_result) 
                # uniformed_test_case = self.uniform(simplified_test_case)
                # new_harness_result = self.config.harness.run_testcase(uniformed_test_case)
                # new_differential_test_result = Result.differential_test(new_harness_result)
                # if len(new_differential_test_result) == 0:
                #     continue
                uniformed_test_case = self.uniform(mutated_test_case)
                new_differential_test_result = harness_result
                self.config.database.insert_differential_test_results(new_differential_test_result, mutated_test_case)                
                self.save_interesting_test_case(uniformed_test_case)
            self.config.database.update_sample_status(sample)  

    def step1(self, size: int):
        """ Step1. Obtain seed programs and mutate. """

        cprint("Step1. Obtain seed programs and mutate.", "blue")
        if size > len(self.config.samples):
            size = len(self.config.samples)
            cprint("The specific size is larger than the number of samples, so we use the number of samples instead.", "yellow")
        for i in range(size):
            sample = self.config.samples[i]
            original_test_case = self.config.callable_processor.get_self_calling(sample)
            print("original_test_case:\n"+original_test_case)
            original_test_case_id = self.config.database.insert_original_testcase(testcase=original_test_case, sample=sample)
            if self.premutation(original_test_case):
                self.config.database.update_sample_status(sample)
                continue
            flag = self.config.database.query_flag(original_test_case_id)
            print(original_test_case_id)
            flag = int(flag, 2)
            mutated_test_case_list = self.mutationByFlag(flag, original_test_case)
   
    def step2(self, size: int):
        """ Step2. Differential testing. """

        # If differential testing is executed separately, we need to obtain the test cases.
        mutated_test_case_list = self.config.database.query_mutated_test_case()
        # Notice that, `mutated_test_case_list` is a tuple list.
        # print(len(mutated_test_case_list))
        cprint("Step2. Differential testing.", "blue")
        if size > len(mutated_test_case_list):
            size = len(mutated_test_case_list)
            cprint("The specific size is larger than the number of samples, so we use the number of samples instead.", "yellow")
        for i in range(size):
            idx, mutated_test_case = mutated_test_case_list[i]
            harness_result = self.config.harness.run_testcase(mutated_test_case)
            print("harness_result:")
            print(harness_result)
            [harness_result, test_case_id] = self.config.database.insert_harness_result(harness_result, idx)
            differential_test_result = Result.differential_test(harness_result)
            print("differential_test_result:")
            for r in differential_test_result:
                print(r)
            if len(differential_test_result) == 0:
                continue
            # TODO. 原本的逻辑是精简后才保存
            self.config.database.insert_differential_test_results(differential_test_result, mutated_test_case)

    def step3(self, size: int):
        """ Step3. Reduce. """

        cprint("Step3. Reduce.", "blue")
        anomalies = self.config.database.query_anomalies()
        if size > len(anomalies):
            size = len(anomalies)
            cprint("The specific size is larger than the number of samples, so we use the number of samples instead.", "yellow")
        for i in range(size):
            anomaly = anomalies[i]
            results = self.config.database.query_harness_result(anomaly[2])
            [suspicious_outputs, normal_outputs] = simplifyTestcaseCore.split_output(results)
            for suspicious_output in suspicious_outputs:
                if anomaly.testbed_id == suspicious_output.testbed_id:
                    current = suspicious_output
                    break
            simplified_test_case = self.config.reducer.reduce(current, normal_outputs)
            uniformed_test_case = self.uniform(simplified_test_case)
            new_harness_result = self.config.harness.run_testcase(uniformed_test_case)
            new_differential_test_result = Result.differential_test(new_harness_result)
            if len(new_differential_test_result) == 0:
                continue
            self.config.database.insert_differential_test_results(new_differential_test_result, mutated_test_case)
            self.save_interesting_test_case(uniformed_test_case)
        self.config.database.update_sample_status(sample)
    
    def premutation(self, original_test_case: str) -> bool:
        """ Filter seed programs that contain syntax errors. """

        harness_result = self.config.harness.run_testcase(original_test_case)
        for output in harness_result.outputs:
            stderr = output.stderr            
            if stderr is None:
                return False
            if "TypeError" not in stderr:
                return False
        return True

    # def mutation(self, original_test_case: str) -> List[str]:
    #     """ Mutate seed programs. """

    #     mutated_test_case_list = []        
    #     mutated_test_case_list.extend(self.config.mutator.mutate(original_test_case, max_size=20))
    #     # Mutate using the folowing mutators in small probability.
    #     rand_num = random.randint(0, 99)
    #     if rand_num < 5:            
    #         temp = self.config.mutator_arrayAndvar.mutate_longArrMethod(original_test_case, max_size=1)
    #         if temp is not None:
    #             mutated_test_case_list.extend(temp)
    #     rand_num1 = random.randint(0, 99)
    #     if rand_num1 < 5:            
    #         temp = self.config.mutator_arrayAndvar.mutate_typearr(original_test_case, max_size=1)
    #         if temp is not None:
    #             mutated_test_case_list.extend(temp)
    #     rand_num2 = random.randint(0, 99)
    #     if rand_num2 < 5:            
    #         mutated_test_case_list.extend(self.config.mutator_regex.mutate_regEx(original_test_case, max_size=1))
    #     mutated_test_case_list.append(original_test_case)
    #     return mutated_test_case_list

    def mutationByFlag(self, flag: int, original_test_case: str) -> List[str]:
        """  Mutate seed programs by querying the flag. """
        
        mutated_test_case_list = []
        # If loop mutator is available, use it to mutate the seed program.
        if LOOP_MUTATOR and (flag & 0b10000 ==0b10000):
            differ=self.getTime(original_test_case)
            if differ > 30:
                mutated_test_case_list.extend(self.config.mutator.mutate(original_test_case, max_size=20))
        # If array mutator is available, use it to mutate the seed program.
        if ARRAY_MUTATOR and (flag & 0b01000 ==0b01000):
            mutated_test_case_list.extend(self.config.mutator.mutateByArray(original_test_case, max_size=1))
        # If regex mutator is available, use it to mutate the seed program.
        if REGEX_MUTATOR and (flag & 0b00100 ==0b00100):
            mutated_test_case_list.extend(self.config.mutator.mutateByRegex(original_test_case, max_size=1))
        # If string mutator is available, use it to mutate the seed program.
        if STRING_MUTATOR and (flag & 0b00010 ==0b00010):
            mutated_test_case_list.extend(self.config.mutator.mutateByString(original_test_case, max_size=1))
        # If object mutator is available, use it to mutate the seed program.
        if OBJECT_MUTATOR and (flag & 0b00001 ==0b00001):
            mutated_test_case_list.extend(self.config.mutator.mutateByObject(original_test_case, max_size=1))
        mutated_test_case_list.append(original_test_case)
        return mutated_test_case_list

    def uniform(self, test_case: str) -> str:
        """ Uniform the variable name of the test case. """

        try:
            uniformed_test_case = self.config.uniform.uniform_variable_name(test_case)
            original_harness_result = self.config.harness.run_testcase(test_case)
            uniformed_harness_result = self.config.harness.run_testcase(uniformed_test_case)
            # If the uniformed test case is still interesting, return it.
            if len(Result.differential_test(original_harness_result)) == len(Result.differential_test(
                    uniformed_harness_result)):
                return uniformed_test_case
        except BaseException as e:
            pass
        return test_case

    def save_interesting_test_case(self, test_case: str):
        """ Use hash code to filter duplicated test cases. """

        hash_code = crypto.md5_str(test_case)
        file_path = (self.config.workspace / f"interesting_testcase/{hash_code}.js").absolute().resolve() 
        file_path.parent.mkdir(parents=True, exist_ok=True) 
        logging.info(f"\nInteresting test case is writen to the file:\n {file_path}")
        file_path.write_text(test_case) 
   
    def getTime(self, originalTestcase:str) -> int:
        """ Get the time difference of the test case. """

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
