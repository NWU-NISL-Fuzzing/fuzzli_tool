import logging
import re
from typing import List

from Result import HarnessResult, DifferentialTestResult
from ResultFilter import getExecptionStatementApi

from ResultFilter.FilterEntities import *
from ResultFilter.errorinfo_classifier.errorinfo_classifier import errorinfo_classify
from ResultFilter.errorinfo_classifier.errorinfo_db_operation import DataBase
from ResultFilter.regex_normalizer import regex_normalization
from utils.getApisFromTestcase import ESAPI
from utils.parseTestbed import TestbedParser


class Classifier:
    def __init__(self, esapi_instance: ESAPI, testbed_parser: TestbedParser, classify_db: DataBase):
        
        self.esapi_instance = esapi_instance
        
        self.testbed_parser = testbed_parser
        
        self.classify_db = classify_db

        
        
        
        self.note_false_positive_counter = 0
        
        self.all_differential_result_filter_types_counter = [0, 0, 0]
        
        self.remained_filter_types_counter = [0, 0, 0]

    
    def filter(self, test_result_list: List[DifferentialTestResult], harness_result: HarnessResult):
        suspicious_result = []
        for test_result in test_result_list:
            [classify_result, test_result.classify_id] = self.is_suspicious_result(test_result.output_id,
                                                                                   harness_result)
            
            test_result.classify_result = classify_result.value

            if classify_result is ClassificationType.SUSPICIOUS_ENGINE_ERROR or \
                    classify_result is ClassificationType.SUSPICIOUS_ENGINE_NO_ERROR or \
                    classify_result is ClassificationType.SUSPICIOUS_ENGINE_NO_ERROR:
                suspicious_result.append(test_result)
        return suspicious_result

    
    def is_suspicious_result(self, index, harness_result: HarnessResult):

        
        key_information = get_key_information(index, harness_result, self.testbed_parser, self.esapi_instance)
        
        
        if key_information[4] == FilterType.TYPE1.value:
            is_false_positive = False
            for engine, exception_info in key_information[2].items():
                if exception_info.__contains__("note: "):
                    is_false_positive = True
            if is_false_positive:
                self.note_false_positive_counter += 1
                
                return [ClassificationType.FALSE_POSITIVE_NOTE, 0]
        
        self.all_differential_result_filter_types_counter[key_information[4] - 1] += 1

        
        
        [suspicious, classify_id] = errorinfo_classify(key_information, self.classify_db)
        if suspicious:
            self.remained_filter_types_counter[key_information[4] - 1] += 1
            
            classify_result = None
            if key_information[4] == FilterType.TYPE3.value:
                classify_result = ClassificationType.SUSPICIOUS_ALL_NO_EXCEPTION_INFO
            elif key_information[4] == FilterType.TYPE2.value:
                classify_result = ClassificationType.SUSPICIOUS_ENGINE_NO_ERROR
            else:
                classify_result = ClassificationType.SUSPICIOUS_ENGINE_ERROR
            return [classify_result, classify_id]
        else:
            
            return [ClassificationType.FALSE_POSITIVE, classify_id]

    def clear_records(self):
        self.classify_db.drop_all_table()

    def print_statistical_results(self):
        logging.info("=======================Filter===================================")
        print("=======================Filter===================================")
        print(f"The number of False positive cause note{self.note_false_positive_counter}")
        logging.info(f"The number of False positive cause note{self.note_false_positive_counter}")
        print(f"First type : {self.all_differential_result_filter_types_counter[0]} pieces,"
              f"Last:{self.remained_filter_types_counter[0]} pieces")
        logging.info(
            f"First type : {self.all_differential_result_filter_types_counter[0]} pieces,"
            f"Last:{self.remained_filter_types_counter[0]} pieces")
        print(f"Second Type{self.all_differential_result_filter_types_counter[1]} pieces,"
              f"Last:{self.remained_filter_types_counter[1]} pieces")
        logging.info(
            f"Second Type{self.all_differential_result_filter_types_counter[1]} pieces,"
            f"Last:{self.remained_filter_types_counter[1]} pieces")
        print(f"Third Type: {self.all_differential_result_filter_types_counter[2]} pieces,"
              f"Last:{self.remained_filter_types_counter[2]} pieces")
        logging.info(
            f"Third Type: {self.all_differential_result_filter_types_counter[2]} pieces,"
            f"Last:{self.remained_filter_types_counter[2]} pieces")
        logging.info("=================================================================")
        print("=================================================================")



def list_normalized_essential_exception_message(outputs_info: str):

    matcher_key_exceptions = list_essential_exception_message(outputs_info)
    
    matcher_key_exceptions = regex_normalization(matcher_key_exceptions)
    return matcher_key_exceptions


def list_essential_exception_message(outputs_info: str):

    regex_error = "(([a-zA-Z]*Error|timeout):.*?)(\\.\\s|\\n|\\.$)"
    regex_hermes_error = "(error:.*?)(\\. |\\n|\\.$)"
    regex_note = "(note:.*?)(\\.\\s|\\n|\\.$)"
    regex_elegent = "[a-zA-Z]+Error:.*"
    
    pattern_error = re.compile(regex_error, re.M)
    pattern_hermes_error = re.compile(regex_hermes_error, re.M)
    pattern_note = re.compile(regex_note, re.M)
    pattern_elegent = re.compile(regex_elegent, re.M)
    
    matcher_error = set([e[0] for e in pattern_error.findall(outputs_info)])
    matcher_hermes_error = set([e[0] for e in pattern_hermes_error.findall(outputs_info)])
    matcher_note = set([e[0] for e in pattern_note.findall(outputs_info)])
    matcher_error_list = list(matcher_error)
    for index in range(len(matcher_error_list)):
        tmp = pattern_elegent.findall(matcher_error_list[index])
        if len(tmp) > 0:
            matcher_error_list[index] = tmp[0]
    matcher = []
    if len(matcher_error) > 0:
        matcher += matcher_error_list
    elif len(matcher_hermes_error) > 0:  
        matcher += matcher_hermes_error
    elif len(matcher_note) > 0:  
        matcher += matcher_note
    matcher_key_exceptions = "\n".join(matcher)
    return matcher_key_exceptions


def get_highest_frequency(target_list: list):
    
    frequency_dic = {e: 0 for e in set(target_list)}
    
    for e in target_list:
        frequency_dic.update({e: frequency_dic.get(e) + 1})
    most_frequent_key = None
    most_frequent_value = -1
    
    for key, value in frequency_dic.items():
        if most_frequent_value < value:
            most_frequent_key = key
            most_frequent_value = value
    return [most_frequent_key, most_frequent_value]



def get_key_information(index, harness_result: HarnessResult, testbed_parser: TestbedParser, esapi_instance: ESAPI):

    suspicious_output = None
    for output in harness_result.outputs:
        if output.id == index:
            suspicious_output = output
    if suspicious_output is None:
        raise Exception("Harness result does not contain special index")
    
    key_exception = list_normalized_essential_exception_message(suspicious_output.stderr + suspicious_output.stdout)
    key_exception_dic = {}
    double_output_id = index
    
    engine_name = testbed_parser.get_engine_name(suspicious_output.testbed)
    no_exception_info_engine_counter = 0
    es_api_node_ast_in_testcase = None
    
    if key_exception != "":
        
        filter_type = FilterType.TYPE1.value
        
        [api_name, es_api_node_ast_in_testcase] = getExecptionStatementApi.get_exception_statement_api(
            esapi_instance,
            harness_result.testcase,
            suspicious_output.stderr + suspicious_output.stdout,
            es_api_node_ast_in_testcase)
        if api_name is None:
            api_name = "NoApi"
        key_exception_dic = {engine_name: key_exception}
    
    else:
        filter_type = FilterType.TYPE2.value
        no_exception_info_engine_counter += 1  
        api_list = []
        for output in harness_result.outputs:
           
            if output.id != index:
                exception_engine_name = testbed_parser.get_engine_name(output.testbed)
                exception_info = list_normalized_essential_exception_message(output.stderr + output.stdout)
               
                if exception_info == "":
                    no_exception_info_engine_counter += 1
               
                key_exception_dic.update({exception_engine_name: exception_info})
                [api, es_api_node_ast_in_testcase] = getExecptionStatementApi.get_exception_statement_api(
                    esapi_instance,
                    harness_result.testcase,
                    output.stderr + output.stdout,
                    es_api_node_ast_in_testcase)

                api = "NoApi" if api is None else api
               
                api_list.append(api)
       
        most_frequent_api, most_frequent_count = get_highest_frequency(api_list)
        if most_frequent_count < len(api_list) * 1 / 2:
            api_name = "NoApi"
        else:
            api_name = most_frequent_api
   
    if no_exception_info_engine_counter == len(harness_result.outputs):
       
        filter_type = FilterType.TYPE3.value
        for output in harness_result.outputs:
            exception_engine_name = testbed_parser.get_engine_name(output.testbed)
            output = output.stderr + output.stdout
            key_exception_dic.update({exception_engine_name: output})
        api_name = "NoApi"
   
    return [double_output_id, engine_name, key_exception_dic, api_name, filter_type]
