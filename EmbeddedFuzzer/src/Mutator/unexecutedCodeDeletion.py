import copy
import pathlib
import re
import tempfile
from typing import Set

from Harness import run_test_case
from utils.JSASTOpt import build_ast, generate_es_code


class CodeRemover:
    def __init__(self, engine: str = "node"):

        
        self.__instrument_template = self.__get_instrument_template()
        
        self.__output_template = "THIS STATEMENT IS EXECUTED TO: "
        self.engine = engine

    def delete_useless_code(self, test_case_ast: dict) -> dict:

        try:
            
            instrumented_test_case_ast = self.instrument(test_case_ast)
            
            instrumented_test_case = generate_es_code(instrumented_test_case_ast)
            
            identifies_set = self.get_executed_statement_identifies(instrumented_test_case)
            
            simplified_test_case_ast = self.remove_instrument(instrumented_test_case_ast, identifies_set)
            return simplified_test_case_ast
        except BaseException as e:
            return test_case_ast

    def instrument(self, test_case_ast: dict) -> dict:

        queue = [test_case_ast]
        instrument_id = 0
        while len(queue) > 0:
            
            node = queue.pop(0)
            
            for key, value in node.items():
                if key == 'type' and value == "VariableDeclaration":
                    for dec in node["declarations"]:
                        if not dec["init"] is None and dec["init"]["type"] == "FunctionExpression":
                            node = dec["init"]["body"]
                            queue.append(node)
                elif type(value) == list and key == "body":
                    
                    child_node_list = value
                    
                    for index in range(len(child_node_list) - 1, -1, -1):
                        
                        queue.append(child_node_list[index])
                        
                        instrument_statement_ast = copy.deepcopy(self.__instrument_template)
                        
                        
                        instrument_statement_ast['expression']['arguments'][0]['value'] = \
                            self.__output_template + str(instrument_id)
                        instrument_id += 1
                        
                        child_node_list.insert(index, instrument_statement_ast)
                elif type(value) == dict and key != "loc":
                    queue.append(value)
        return test_case_ast

    def get_executed_statement_identifies(self, test_case: str) -> Set[str]:

        
        identifies_set = set()
        
        
        with tempfile.NamedTemporaryFile(prefix="javascriptTestcase_", suffix=".js", delete=True) as f:
            test_case_path = pathlib.Path(f.name)
            test_case_path.write_text(test_case)
            
            output = run_test_case(self.engine, test_case_path)
            info = output.stdout + output.stderr
        
        
        
        pattern = re.compile(self.__output_template + "(\\d+)$")
        for line in info.split("\n"):
            
            if not pattern.match(line) is None:
                identifies_set.add(line)
        return identifies_set

    @staticmethod
    def remove_instrument(test_case_ast: dict, identifies: set) -> dict:

        queue = [test_case_ast]
        while len(queue) > 0:
            node = queue.pop(0)
            for key, value in node.items():
                if key == 'type' and value == "VariableDeclaration":
                    for dec in node["declarations"]:
                        if not dec["init"] is None and dec["init"]["type"] == "FunctionExpression":
                            node = dec["init"]["body"]
                            queue.append(node)
                elif type(value) == list and key == "body":
                    child_node_list = value
                    
                    for index in range(len(child_node_list) - 2, -1, -2):
                        
                        if not identifies.__contains__(child_node_list[index]['expression']['arguments'][0]['value']):
                            del child_node_list[index]  
                            del child_node_list[index]  
                            continue
                        
                        del child_node_list[index]  
                        queue.append(child_node_list[index])
                elif type(value) == dict and key != "loc":
                    queue.append(value)
        return test_case_ast

    @staticmethod
    def __get_instrument_template():

        code = """console.log("")"""
        return build_ast(code)["body"][0]
