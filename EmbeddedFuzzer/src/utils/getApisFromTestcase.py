import collections
import copy
import logging
import pathlib
import re
import tempfile

import Harness
import execjs

Callee = collections.namedtuple('Callee', [  
    'callee_object', 'callee_method', 'callee_object_type'
])


def get_function_nodes_from_testcase(testcase):
    get_all_function_nodes = execjs.compile("""
            let estraverse = require('estraverse');
            let esprima = require('esprima');
            let fs = require("fs");

            function analyzeCode(filename) {  
                var code = fs.readFileSync(filename).toString();
                var ast = esprima.parseScript(code,{ loc: true });

                var nodes = [];
                estraverse.traverse(ast, {  
                    enter: function (node) { 
                        // Array.prototype.toString() or Math.abs()
                        if (node.type == "CallExpression" && node.callee.type === "MemberExpression" && node.callee.property.type === 'Identifier') { 
                            nodes[nodes.length] = node;

                        }
                        // new Array()
                        else if (node.type == "NewExpression" && node.callee.type === "Identifier"){
                            nodes[nodes.length] = node;
                        } 
                        // parseInt(), Object(), print()
                        else if (node.type == "CallExpression" && node.callee.type === "Identifier"){
                            nodes[nodes.length] = node;
                        }
                    }   
                }); 
                return nodes	
            }        
        """)
    with tempfile.NamedTemporaryFile(prefix="javascriptTestcase_", suffix=".js", delete=True) as f:
        test_case_path = pathlib.Path(f.name)
        test_case_path.write_text(testcase)
        nodes = get_all_function_nodes.call("analyzeCode", str(test_case_path))
    return nodes


def run_testcase(testbed: str, testcase: str) -> str:
    with tempfile.NamedTemporaryFile(prefix="javascriptTestcase_", suffix=".js", delete=True) as f:
        testcase_path = pathlib.Path(f.name)
        testcase_path.write_text(testcase)
        output = Harness.run_test_case(testbed=testbed, testcase_path=testcase_path)
    return output.stdout + output.stderr


class ESAPI:
    def __init__(self, config, testbed="node"):
        self.check_dependencies()  
        self.testbed = testbed  
        self.constructorAPIS = self.initial_es_apis(config["constructor"])
        self.functionAPIS = self.initial_es_apis(config["function"]) + self.constructorAPIS
        self.classMethodAPIs = self.initial_es_apis(config["classMethod"])
        self.prototypeMethodAPIs = self.initial_es_apis(config["prototypeMethod"])
        self.constructors_in_testcases = []
        self.functions_in_testcases = []
        self.class_methods_in_testcases = []
        self.prototype_methods_in_testcases = []

    @staticmethod
    def check_dependencies():
        foo = execjs.compile("""
                    let estraverse = require('estraverse');
                    let esprima = require('esprima');
                    let escodegen = require('escodegen');
                    let fs = require("fs");

                    function analyzeCode() {
                        return null;
                    }        
                """)
        try:
            foo.call("analyzeCode")
        except BaseException as e:
            raise ImportError(str(e) + f"\nTry to install the module with command \"npm install ...\" ")

    def get_es_apis_in_testcases(self):
        return self.constructors_in_testcases + self.functions_in_testcases + self.class_methods_in_testcases + \
               self.prototype_methods_in_testcases

    def api_info(self, callee: Callee) -> list:
        """
        :param callee:
        :return: [is ECMAScript-262 API, API name, API type]
        """
        class_method = self.is_class_method(callee)
        if class_method[0] is True:
            return class_method
        return self.is_instance_method(callee)

    def is_class_method(self, callee: Callee) -> list:
        for method in self.classMethodAPIs:
            if method == callee.callee_object + "." + callee.callee_method:
                return [True, method, "classMethod"]
        return [False, None, None]

    def is_instance_method(self, callee: Callee) -> list:
        method_in_testcase = callee.callee_object_type + ".prototype." + callee.callee_method
        if ["Function.prototype.apply", "Function.prototype.call"].__contains__(method_in_testcase) and \
                self.prototypeMethodAPIs.__contains__(callee.callee_object):
            return [True, callee.callee_object + "." + callee.callee_method, "prototypeMethod"]
        if self.prototypeMethodAPIs.__contains__(method_in_testcase):
            return [True, method_in_testcase, "prototypeMethod"]
        if callee.callee_object == "GeneratorFunction":
            return [True, "Generator.prototype." + callee.callee_method, "prototypeMethod"]
        if ["Int8Array", "Uint8Array", "Uint8ClampedArray", "Int16Array", "Uint16Array", "Int32Array", "Uint32Array",
            "Float32Array", "Float64Array"].__contains__(callee.callee_object):
            return [True, "%TypedArray.prototype%." + callee.callee_method, "prototypeMethod"]
        return [False, None, None]

    def is_constructor_function(self, candidate_api_name: str) -> bool:
        if self.constructorAPIS.__contains__(candidate_api_name):
            return True
        return False

    def is_function(self, candidate_api_name: str) -> bool:
        if self.functionAPIS.__contains__(candidate_api_name):
            return True
        return False

    def parse_function_nodes(self, test_case_code: str):

        es_api_nodes = []
        try:
            
            nodes = get_function_nodes_from_testcase(test_case_code)
        except Exception as e:
            logging.warning(e)
            return es_api_nodes
        split_test_case = test_case_code.split("\n")
        for node in nodes:
            
            if node["type"] == "NewExpression" and node["callee"]["type"] == "Identifier":
                constructor_name = node["callee"]["name"]
                if self.is_constructor_function(constructor_name):
                    self.constructors_in_testcases.append(constructor_name)
                    node["ESAPI"] = {"type": "constructor", "name": constructor_name}
                    es_api_nodes.append(node)
                    continue
            
            elif node["type"] == "CallExpression" and node["callee"]["type"] == "Identifier":
                function_name = node["callee"]["name"]
                if self.is_function(function_name):
                    self.functions_in_testcases.append(function_name)
                    node["ESAPI"] = {"type": "function", "name": function_name}
                    es_api_nodes.append(node)
                    continue
            
            if node["type"] == "CallExpression" and node["callee"]["type"] == "MemberExpression" \
                    and node["callee"]["property"]["type"] == 'Identifier':
                object_loc = node["callee"]["object"]["loc"]
                
                start_index = int(object_loc["start"]["line"]) - 1
                callee_object = self.get_callee_object(split_test_case, object_loc)
                method = node["callee"]["property"]["name"]
                type_reference_statement = f"console.log('The type of the callee object is: '" \
                                           f" + Object.prototype.toString.call(({callee_object})))"
                pattern = r"(The type of the callee object is: \[object )(.*)(\]\n)"
                tmp_test_case = copy.deepcopy(split_test_case)
                tmp_test_case.insert(start_index, type_reference_statement)
                output = run_testcase(self.testbed, "\n".join(tmp_test_case))  
                search_result = re.search(pattern, output)
                if search_result is None:
                    continue
                callee_object_type = search_result.group(2)
                [is_es_api, full_method_name, api_type] = self.api_info(Callee(callee_object, method, callee_object_type))
                if is_es_api:
                    if api_type == "prototypeMethod":
                        self.prototype_methods_in_testcases.append(full_method_name)
                    else:
                        self.class_methods_in_testcases.append(full_method_name)
                    node["ESAPI"] = {"type": api_type, "name": full_method_name}
                    es_api_nodes.append(node)
        return es_api_nodes

    @staticmethod
    def get_callee_object(testcase, object_loc):

        
        start_line = int(object_loc["start"]["line"]) - 1
        end_line = int(object_loc["end"]["line"]) - 1
        start_column = int(object_loc["start"]["column"])
        end_column = int(object_loc["end"]["column"])
        if start_line != end_line:
            callee_object = [testcase[start_line][start_column:]]
            callee_object += testcase[start_line + 1: end_line]
            callee_object += [testcase[end_line][:end_column]]
            return "\n".join(callee_object)
        callee_object = testcase[start_line][start_column: end_column]
        return callee_object

    @staticmethod
    def initial_es_apis(file_path: str) -> list:
        with open(file_path) as f:
            apis = f.read().strip().split("\n")
        return [API.replace("()", "") for API in apis]

    @staticmethod
    def count_es_apis_in_testcase(nodes):
        es_apis = {"constructor": 0, "function": 0, "classMethod": 0, "prototypeMethod": 0}
        for node in nodes:
            es_apis[node["ESAPI"]["type"]] += 1
        return es_apis

    def statistical_apis_frequency(self):
        es_apis_in_all_test_case = self.get_es_apis_in_testcases()
        fre = {}
        non_repeat_api = set(es_apis_in_all_test_case)
        for e in non_repeat_api:
            fre[e] = 0
        for api in es_apis_in_all_test_case:
            fre[api] += 1
        return fre
