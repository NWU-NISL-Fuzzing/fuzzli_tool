import logging
import math
import time

import Result
import jsbeautifier
from Reducer import reduce_by_line, simplifyTestcaseCore
from utils.JSASTOpt import build_ast, generate_es_code

start_time = time.time()

class Reducer:
    def __init__(self, multi_threads: bool = True):
        self.test_case_ast = None
        self.harness_result = None
        self.multi_threads = multi_threads

        
        self.mutated_harness_result_list = None

    def reduce(self, harness_result: Result.HarnessResult) -> str:

        self.harness_result = harness_result
        self.mutated_harness_result_list = []  
        original_test_case = harness_result.testcase.strip()
        try:
            self.test_case_ast = build_ast(original_test_case)
        except Exception as r:
            
            logging.info("Failed to extract AST. ")
            [simplified_test_case, new_bugs_list] = reduce_by_line.sample_by_statement(harness_result)
            self.mutated_harness_result_list = new_bugs_list
            return self.beautify_test_case(simplified_test_case)

        self.traverse(self.test_case_ast)  
        
        self.peeling(self.test_case_ast)  
        return generate_es_code(self.test_case_ast)

    def traverse(self, node: dict, lithium_algorithm=False):

        end_time = time.time()
        duration = end_time - start_time
        if duration > 6000:
            return

        
        for key, values in reversed(list(node.items())):
            
            if type(values) == list:
                
                remained = 1 if key == "declarations" else 0
                
                if lithium_algorithm:
                    self.ddmin(values, remained)
                else:
                    
                    
                    if len(values) > 1:
                        node[key] = []
                        [removable, new_bug] = self.removable()
                        if new_bug is not None:
                            self.mutated_harness_result_list.append(new_bug)
                        if removable:
                            continue
                        else:
                            
                            node[key] = values
                    
                    for index in range(len(values) - 1, -1, -1):
                        
                        tmp_node = values.pop(index)
                        [removable, new_bug] = self.removable()
                        if new_bug is not None:
                            self.mutated_harness_result_list.append(new_bug)
                        if removable:
                            continue
                        else:
                            
                            values.insert(index, tmp_node)
                            
                            self.traverse(tmp_node)
            
            elif values is not None and type(values) == dict and key != "loc":
                self.traverse(values)  

    def ddmin(self, arr: list, remained: int):

        size = len(arr)
        if size == 0:
            return
        
        chunk_size = 2 ** int(math.log2(size))
        while chunk_size >= 1:
            
            size = len(arr)
            for index in range(size - chunk_size, -1, -chunk_size):
                if len(arr) <= remained:  
                    self.traverse(arr[index])
                    return
                logging.debug(f"Try to deleting:{index} - {index + chunk_size}")
                
                tmp_deleted = multi_pop(arr, index, index + chunk_size)
                
                [removable, new_bug] = self.removable()
                if new_bug is not None:
                    self.mutated_harness_result_list.append(new_bug)
                if not removable:  
                    
                    multi_push(arr, index, tmp_deleted)
                    
                    if chunk_size == 1:
                        self.traverse(arr[index])
            
            chunk_size = chunk_size >> 1

    def peeling(self, test_case_ast: dict):

        queue = [test_case_ast]
        while len(queue) > 0:
            node = queue.pop(0)
            
            for key, value in node.items():
                if key == 'type' and value == "VariableDeclaration":
                    for dec in node["declarations"]:
                        if not dec["init"] is None and dec["init"]["type"] == "FunctionExpression":
                            queue.append(dec["init"]["body"])
                elif type(value) == list and key == "body":
                    child_node_list = value
                    for index in range(len(child_node_list) - 1, -1, -1):
                        
                        
                        tmp_node = child_node_list[index]
                        try:
                            if tmp_node["type"] == "ForStatement" \
                                    and tmp_node["init"]["declarations"][0]["id"]["name"] == "INDEX":
                                
                                
                                child_node_list[index] = tmp_node["body"]["body"][0]
                                removable = self.removable()[0]
                                if removable:
                                    return
                                else:
                                    
                                    child_node_list[index] = tmp_node
                        except BaseException as e:
                            child_node_list[index] = tmp_node
                            pass
                        queue.append(child_node_list[index])
                elif type(value) == dict and key != "loc":
                    queue.append(value)

    def removable(self):

        try:
            tmp_code = generate_es_code(self.test_case_ast)
        except BaseException as e:
            return [False, None]
        
        return simplifyTestcaseCore.is_removable(self.harness_result, tmp_code)

    @staticmethod
    def beautify_test_case(test_case: str) -> str:

        beautified_test_case = str(test_case).split("\n")
        for index in range(len(beautified_test_case) - 1, -1, -1):
            if beautified_test_case[index].strip() == '':
                beautified_test_case.pop(index)
        beautified_test_case = "\n".join(beautified_test_case)
        return jsbeautifier.beautify(beautified_test_case)


def multi_pop(arr: list, start: int, end: int):
    deleted_arr = []
    for num in range(end - start):
        deleted_arr.append(arr.pop(start))
    return deleted_arr


def multi_push(arr: list, start: int, to_added: list):
    for tmp_index in range(len(to_added) - 1, -1, -1):
        arr.insert(start, to_added[tmp_index])
