import copy
import logging
import sys
from typing import List

from Mutator.unexecutedCodeDeletion import CodeRemover

from utils.JSASTOpt import *



sys.path.extend(['../EmbeddedFuzzer/src/Postprocessor','../EmbeddedFuzzer/src/Mutator'])
from callable_type import CallableProcessor
from Mutate_object import Mutate_Object
from Mutate_regx import Mutate_RegExp
from Mutate_string import Mutate_String
from Mutate_array import Mutate_Array





class Timer:
    def __init__(self, start: dict, end: dict, output: dict):
        
        self.start_timer_js_ast = start
        self.end_timer_js_ast = end
        self.output_js_ast = output


class Mutator:
    def __init__(self, engine: str = "node", max_size: int = 5):
        
        self.loop_structure_ast_template = self.get_loop_structure_ast(1000)
        
        self.timer_template = self.get_plug_in_timer()
        
        self.codeRemover = CodeRemover(engine)
        self.max_size = max_size  

    
    def mutateByObject(self, test_case_code: str, max_size: int = 5) -> List[str]:
        self.max_size = max_size
        try:
            result = Mutate_Object().mutateObject(test_case_code, max_size)
        except BaseException as e:
            logging.debug(f"Failed to mutation.\n {str(e)}")
            return []
        return result

    
    def mutateByRegex(self, test_case_code: str, max_size: int = 5) -> List[str]:
        self.max_size = max_size
        try:
            result = Mutate_RegExp().mutateRegex(test_case_code, max_size)
        except BaseException as e:
            logging.debug(f"Failed to mutation.\n {str(e)}")
            return []
        return result

    
    def mutateByString(self, test_case_code: str, max_size: int = 5) -> List[str]:
        self.max_size = max_size
        try:
            result = Mutate_String().mutateString(test_case_code, max_size)
        except BaseException as e:
            logging.debug(f"Failed to mutation.\n {str(e)}")
            return []
        return result

    
    def mutateByArray(self, test_case_code: str, max_size: int = 5) -> List[str]:
        self.max_size = max_size
        try:
            result = Mutate_Array().mutateArray(test_case_code, max_size)
        except BaseException as e:
            logging.debug(f"Failed to mutation.\n {str(e)}")
            return []
        return result


    
    def mutate(self, test_case_code: str, max_size: int = 5) -> List[str]:

        self.max_size = max_size
        
        try:
            test_case_ast = build_ast(test_case_code)
        except BaseException as e:
            
            logging.debug(f"Failed to extract AST.\n {str(e)}")
            return []
        
        optimized_test_case_ast = self.codeRemover.delete_useless_code(test_case_ast)
        return self.add_loop_surrounding_statement(optimized_test_case_ast)

    def add_loop_surrounding_statement(self, test_case_ast: dict) -> List[str]:

        mutated_test_case_list = []
        loop_type = {'ForStatement', 'ForInStatement', 'WhileStatement', 'ForOfStatement', 'DoWhileStatement'}
        if len(test_case_ast["body"]) == 0:
            return mutated_test_case_list
        queue = [test_case_ast]
        while len(queue) > 0:
            node = queue.pop(0)
            for key, value in node.items():
                if key == 'type' and loop_type.__contains__(value):
                    break
                if key == 'type' and value == "VariableDeclaration":
                    for dec in node["declarations"]:
                        if not dec["init"] is None and dec["init"]["type"] == "FunctionExpression":
                            node = dec["init"]["body"]
                            queue.append(node)
                elif type(value) == list and key == "body":
                    child_node_list = value
                    for index in range(len(child_node_list)):  
                        queue.append(child_node_list[index])
                        
                        node_list_deepcopy = copy.deepcopy(child_node_list)
                        
                        node_list_deepcopy = self.add_loop(node_list_deepcopy, index)
                        
                        node[key] = node_list_deepcopy
                        mutated_test_case = generate_es_code(copy.deepcopy(test_case_ast))  
                        
                        mutated_test_case_list.append(mutated_test_case)
                        node[key] = child_node_list  
                        
                        if len(mutated_test_case_list) >= self.max_size:
                            return mutated_test_case_list
                elif type(value) == dict and key != "loc":
                    queue.append(value)
        return mutated_test_case_list

    def add_loop(self, node_list: list, index: int) -> list:

        loop_wrapped_node = copy.deepcopy(self.loop_structure_ast_template)
        
        loop_wrapped_node["body"]["body"].append(node_list[index])
        node_list[index] = loop_wrapped_node
        return node_list

    def add_timer(self, node_list: list, index: int) -> list:

        node_list.insert(index + 1, self.timer_template.output_js_ast)
        node_list.insert(index + 1, self.timer_template.end_timer_js_ast)
        node_list.insert(index, self.timer_template.start_timer_js_ast)
        return node_list

    @staticmethod
    def get_loop_structure_ast(cycles: int):

        code = """for (var INDEX=0; INDEX<10; INDEX++) {}
        """
        ast = build_ast(code)
        loop_structure_ast = ast["body"][0]
        loop_structure_ast["test"]["right"]["value"] = cycles
        return loop_structure_ast

    @staticmethod
    def get_plug_in_timer() -> Timer:

        code = """
        var startTimestamp = (new Date()).getTime();
        var endTimestamp = (new Date()).getTime();
        print("EmbeddedFuzzerTimer:" + (endTimestamp - startTimestamp) + "ms");
        """
        ast = build_ast(code)
        return Timer(ast["body"][0], ast["body"][1], ast["body"][2])

    '''
    def get_array_mutation(test_case) -> str:
        
        start, _, end = test_case.partition('\n')
        dfarray1 = "var arr = [123.1556,-3334.223452,3.14159265358979322,7,9];"
        dfarray2 = "var arr = new Array(Number.MAX_VALUE,Number.MIN_VALUE,6,8,10);"
        dfarray3 = "var arr = new Array(5); \narr[0] = 1; \narr[1] = 2; \narr[2] = 3; \narr[3] = 4; \narr[4] = 5;"
        
        dfarray4 = "var arr = new Array((Math.pow(2,53)),4,6,8,10);"
        dfarray5 = "var arr = new Array((Math.pow(2,53)+1),4,6,8,10)"
        
        dfarray6 = "var arr = new Array(Math.pow(2,32)-1);"
        dfarray7 = "var arr = new Array(Math.pow(2,32));"
        
        dfarray8 = "var arr = new Array('dd/n&^\/%$
        
        dfarray9 = "var arr = Array.from(\"ABCDEFG\");"
        
        dfarray10 = "var arr = new Array(Number.MAX_VALUE+1,Number.MIN_VALUE-1,6,undefined,10);"
        dfarray11 = "var arr = new Array(true,false,6,undefined,10);"
        dfarray12 = "var arr = new Array(true,null,6,undefined,10);"
        dfarray13 = "var arr = new Array(5);\narr[0] = 3.4327; \narr[1] = 2; \narr[2] = -3.56443; \narr[3] = undefined; \narr[4] = false;"
        dfarray14 = "var arr = [];\nfor(var i=0;i<100000;i++){\narr[i] = i;\n}"
        arr1 = random.choice([dfarray1, dfarray2, dfarray3, dfarray4, dfarray5, dfarray6, dfarray7, dfarray8, dfarray9, dfarray10, dfarray11, dfarray12, dfarray13, dfarray14])

        
        arrayop1 = "arr.join(); \narr.join('-');
        
        arrayop2 = "var count = arr.push('d','e'); 
       
        arrayop3 = "var item = arr.pop();\nvar item2 = arr.pop('c','d');"
       
        arrayop4 = "var count = arr.unshift('a','b');"
       
        arrayop5 = "var item = arr.shift();"
       
        arrayop6 = "arr.sort();"
       
        arrayop7 = "arr.reverse();"
       
        arrayop8 = "var arrCopy = arr.concat(9,[11,13]);"
        arrayop9 = "var arrCopy = arr.concat([9,[11,13]]);"
       
        arrayop10 = "var arrCopy = arr.slice(1); \nvar arrCopy2 = arr.slice(1,4); \nvar arrCopy3 = arr.slice(1,-2); \nvar arrCopy4 = arr.slice(-4,-2);"
       
        arrayop11 = "var arrRemoved = arr.splice(0,2);"
        arrayop12 = "var arrRemoved = arr.splice(2,0,4,6);"
        arrayop13 = "var arrRemoved = arr.splice(1,1,2,4);"
       
        arrayop14 = "arr.indexOf(5); \narr.lastIndexOf(5);"
        arrayop15 = "arr.indexOf(5,2); \narr.lastIndexOf(5,4);"
       
        arrayop16 = "for(var i=0;i<arr.length;i++){\nvar j = arr[i];\n}"
       
        arrayop17 = "var sum  = arr.reduce(function(pre,cur,index,array){\nreturn pre + cur;\n})"
        arrayop18 = "arr.forEach(function(item,index,arr) {\nvar j = item+'-'+index+'-'+arr;\n})"
        arrayop19 = "var b = arr.some(function (value) {\nreturn value > 3;\n})\nlet c = arr.some(function(value,index,arr) {\nreturn value > 2 && value > 2\n})"            
        arrayop20 = "var b = arr.every(function(value) {\nreturn value >  3;\n})"
        arrayop21 = "var a = arr.filter(function (value) {\nreturn value > 3;\n})\na[1] = 100;"
        arrayop22 = "var a = arr.map(function (value) {\nreturn value * 3;\n});\na[1] = 100;"
       
        arrayop23 = "arr.toString();"
        arrayop24 = "arr[arr.length] = 'Kiwi';"
        arrayop25 = "delete arr[0];"
        arrayop26 = "arr.copyWithin(2, 0);"
        arrayop27 = "var f = arr.entries();\nfor (x of f) {\ndocument.getElementById(\"demo\").innerHTML += x;\n}"
        arrayop28 = "var n = arr.includes(\"Mango\");"
        arrayop29 = "var fk = arr.keys();\nfor (x of fk) {\ndocument.getElementById(\"demo\").innerHTML += x + \"<br>\";\n}"
        arrayop30 = "arr.fill(\"Kiwi\");"
        arr2 = np.random.choice([arrayop1, arrayop2, arrayop3, arrayop4, arrayop5, arrayop6, arrayop7, arrayop8, arrayop9, arrayop10, arrayop11, arrayop12, arrayop13, arrayop14, arrayop15, arrayop16, arrayop17, arrayop18, arrayop19, arrayop20, arrayop21, arrayop22, arrayop23, arrayop24, arrayop25, arrayop26, arrayop27, arrayop28, arrayop29, arrayop30], p=[0.03, 0.05, 0.05, 0.05, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.05, 0.05, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.05, 0.01, 0.03, 0.03, 0.03])
       

       
        loop1 = "for(var i = 0; i < 10000; i++){\n"
        loop2 = "}\n"
       
        result = start+"\n"+arr1+"\n"+loop1+arr2+"\n"+loop2+end

        return result

    def get_globalvar_mutation(test_case) -> str:
       
       
        start1, _, end1 = test_case.partition('\n')
        start2, _, end = end1.partition('\n')
        start = start1+start2
        typemu = "    //Global Variable Variation"
        var1 = "    name = 'hsq';"
        var2 = "    name = [1,3,5,7,9];"
        var3 = "    name = new Array(Math.pow(2,32)-1);"
        arr1 = random.choice([var1, var2, var3])
        arr2 = "nn = name;"
        result = start+"\n"+typemu+"\n"+arr1+"\n"+end+"\n"+arr2
        return result


    def get_addarray(testcase,types,params) -> str:
       
       
        start1, _, end1 = testcase.partition('\n')
        start2, _, end = end1.partition('\n')
        start = start1+start2

        typemu = "    //Array mutation"

        arrayop1 = "    arr.join();\n    arr.join('-');"
       
        arrayop2 = "    var count = arr.push('d','e');"
       
        arrayop3 = "    arr.pop();\n    arr.pop('c','d');"
       
        arrayop4 = "    var count = arr.unshift('a','b');"
       
        arrayop5 = "    arr.shift();"
       
        arrayop6 = "    arr.sort();"
       
        arrayop7 = "    arr.reverse();"
       
        arrayop8 = "    arr.concat(9,[11,13]);"
        arrayop9 = "    arr.concat([9,[11,13]]);"
       
        arrayop10 = "    arr.slice(1);\n    arr.slice(1,4);\n    arr.slice(1,-2);\n    arr.slice(-4,-2);"
       
        arrayop11 = "    arr.splice(0,2);"
        arrayop12 = "    arr.splice(2,0,4,6);"
        arrayop13 = "    arr.splice(1,1,2,4);"
       
        arrayop14 = "    arr.indexOf(5);\n    arr.lastIndexOf(5);"
        arrayop15 = "    arr.indexOf(5,2);\n    arr.lastIndexOf(5,4);"
       
        arrayop16 = "    for(var i=0;i<arr.length;i++){\n        var j = arr[i];\n    }"
       
        arrayop17 = "    var sum  = arr.reduce(function(pre,cur,index,array){\n        return pre + cur;\n    })"
        arrayop18 = "    arr.forEach(function(item,index,arr) {\n        var j = item+'-'+index+'-'+arr;\n    })"
        arrayop19 = "    var b = arr.some(function (value) {\n        return value > 3;\n    })\n    let c = arr.some(function(value,index,arr) {\n        return value > 2 && value > 2\n    })"            
        arrayop20 = "    var b = arr.every(function(value) {\n        return value >  3;\n    })"
        arrayop21 = "    var a = arr.filter(function (value) {\n        return value > 3;\n    })\n    a[1] = 100;"
        arrayop22 = "    var a = arr.map(function (value) {\n        return value * 3;\n    });\n    a[1] = 100;"
       
        arrayop23 = "    arr.toString();"
        arrayop24 = "    arr[arr.length] = 'Kiwi';"
        arrayop25 = "    delete arr[0];"
        arrayop26 = "    arr.copyWithin(2, 0);"
        arrayop27 = "    var f = arr.entries();\n    for (x of f) {\n        document.getElementById(\"demo\").innerHTML += x;\n    }"
        arrayop28 = "    var n = arr.includes(\"Mango\");"
        arrayop29 = "    var fk = arr.keys();\n    for (x of fk) {\n        document.getElementById(\"demo\").innerHTML += x + \"<br>\";\n    }"
        arrayop30 = "    arr.fill(\"Kiwi\");"
        arr1 = np.random.choice([arrayop1, arrayop2, arrayop3, arrayop4, arrayop5, arrayop6, arrayop7, arrayop8, arrayop9, arrayop10, arrayop11, arrayop12, arrayop13, arrayop14, arrayop15, arrayop16, arrayop17, arrayop18, arrayop19, arrayop20, arrayop21, arrayop22, arrayop23, arrayop24, arrayop25, arrayop26, arrayop27, arrayop28, arrayop29, arrayop30], p=[0.03, 0.05, 0.05, 0.05, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.05, 0.05, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.05, 0.01, 0.03, 0.03, 0.03])
        result = start + '\n' +typemu
        j = 0
        z = 0
        for vartype in types:
            j = j+1
            if vartype == ['array']:
                z = z+1
               
                param = params[j-1]
                muarr = arr1.replace('arr', param)
                result = result + '\n' +muarr
               

        if z>0:
            result = result + '\n' + end
            return result
        else:
            return "false"


    def get_looparray(testcase,types,params) -> str:
       
       
        start1, _, end1 = testcase.partition('\n')
        start2, _, end = end1.partition('\n')
        start = start1+start2

        typemu = "    

        arrayop1 = "    arr.join();\n    arr.join('-');"
       
        arrayop2 = "    var count = arr.push('d','e');"
       
        arrayop3 = "    arr.pop();\n    arr.pop('c','d');"
       
        arrayop4 = "    var count = arr.unshift('a','b');"
       
        arrayop5 = "    arr.shift();"
       
        arrayop6 = "    arr.sort();"
       
        arrayop7 = "    arr.reverse();"
       
        arrayop8 = "    arr.concat(9,[11,13]);"
        arrayop9 = "    arr.concat([9,[11,13]]);"
       
        arrayop10 = "    arr.slice(1);\n    arr.slice(1,4);\n    arr.slice(1,-2);\n    arr.slice(-4,-2);"
       
        arrayop11 = "    arr.splice(0,2);"
        arrayop12 = "    arr.splice(2,0,4,6);"
        arrayop13 = "    arr.splice(1,1,2,4);"
       
        arrayop14 = "    arr.indexOf(5);\n    arr.lastIndexOf(5);"
        arrayop15 = "    arr.indexOf(5,2);\n    arr.lastIndexOf(5,4);"
       
        arrayop16 = "    for(var i=0;i<arr.length;i++){\n        var j = arr[i];\n    }"
       
        arrayop17 = "    var sum  = arr.reduce(function(pre,cur,index,array){\n        return pre + cur;\n    })"
        arrayop18 = "    arr.forEach(function(item,index,arr) {\n        var j = item+'-'+index+'-'+arr;\n    })"
        arrayop19 = "    var b = arr.some(function (value) {\n        return value > 3;\n    })\n    let c = arr.some(function(value,index,arr) {\n        return value > 2 && value > 2\n    })"            
        arrayop20 = "    var b = arr.every(function(value) {\n        return value >  3;\n    })"
        arrayop21 = "    var a = arr.filter(function (value) {\n        return value > 3;\n    })\n    a[1] = 100;"
        arrayop22 = "    var a = arr.map(function (value) {\n        return value * 3;\n    });\n    a[1] = 100;"
       
        arrayop23 = "    arr.toString();"
        arrayop24 = "    arr[arr.length] = 'Kiwi';"
        arrayop25 = "    delete arr[0];"
        arrayop26 = "    arr.copyWithin(2, 0);"
        arrayop27 = "    var f = arr.entries();\n    for (x of f) {\n        document.getElementById(\"demo\").innerHTML += x;\n    }"
        arrayop28 = "    var n = arr.includes(\"Mango\");"
        arrayop29 = "    var fk = arr.keys();\n    for (x of fk) {\n        document.getElementById(\"demo\").innerHTML += x + \"<br>\";\n    }"
        arrayop30 = "    arr.fill(\"Kiwi\");"
        arr1 = np.random.choice([arrayop1, arrayop2, arrayop3, arrayop4, arrayop5, arrayop6, arrayop7, arrayop8, arrayop9, arrayop10, arrayop11, arrayop12, arrayop13, arrayop14, arrayop15, arrayop16, arrayop17, arrayop18, arrayop19, arrayop20, arrayop21, arrayop22, arrayop23, arrayop24, arrayop25, arrayop26, arrayop27, arrayop28, arrayop29, arrayop30], p=[0.03, 0.05, 0.05, 0.05, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.05, 0.05, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.05, 0.01, 0.03, 0.03, 0.03])
        loop1 = "for(var i = 0; i < 100000; i++){"
        loop2 = "}"
        result = start + '\n' + typemu + '\n' + loop1
        j = 0
        z = 0
        for vartype in types:
            j = j+1
            if vartype == ['array']:
                z = z+1
               
                param = params[j-1]
                muarr = arr1.replace('arr', param)
                result = result + '\n' +muarr
               

        if z>0:
            result = result + '\n' + loop2 + '\n' + end
            return result
        else:
            return "false"
    

   
    def recurarrdef(testcase) -> str:
       
       
        start1, _, end1 = testcase.partition('\n')
        start2, _, end = end1.partition('\n')
        start = start1+start2
       
        part2temp = str(re.findall(r'[(](.*?)[)]', start))
        _, __, part2temp2 = part2temp.partition('\'')
        part2, _, __ = part2temp2.partition('\'')

       
        start1, _, end1 = start.partition(')')
       
        typemu = "    //Recursively defining ultra long type array mutations"
       
        part1="\n    if(n==1){\n        return 0;\n    }"
        
        start = start1+", n"+_+end1+"\n"+typemu+part1


       
       
        def1 = "    var v0 = new Float64Array(1000000);"
        def2 = "    var v0 = new Float32Array(1000000);"
        def3 = "    var v0 = new Int8Array(1000000);"
        def4 = "    var v0 = new Uint8Array(1000000);"
        def5 = "    var v0 = new Uint8ClampedArray(1000000);"
        def6 = "    var v0 = new Int16Array(1000000);"
        def7 = "    var v0 = new Uint16Array(1000000);"
        def8 = "    var v0 = new Int32Array(1000000);"
        def9 = "    var v0 = new Uint32Array(1000000);"
        def10 = "    var v0 = new BigInt64Array(1000000);"
        def11 = "    var v0 = new BigUint64Array(1000000);"
        def12 = "    var v0 = new ArrayBuffer(1000000);"
        arr1 = random.choice([def1, def2, def3, def4, def5, def6, def7, def8, def9, def10, def11, def12])
        part2 ="    NISLFuzzingFunc("+part2+", n-1);"
        result = start + '\n' +arr1 + '\n' + part2

        end1, _, end2 = end.rpartition('\n')
        end1, _, end3 = end1.rpartition('\n')
        part3 = "\nvar n = 10000;"

       
        part4, _, __ = end3.partition(')')
        part4 = part4 + ", n);"
        end = end1+part3+"\n"+part4+"\n"+end2

        result = result + '\n' + end
        return result
    '''

class Mutator_arrayAndvar:
    def __init__(self, engine: str = "node", max_size: int = 3):
        self.max_size = max_size 
    
   
    '''
    def mutate_array(self, test_case_code: str, max_size: int = 3) -> List[str]:

        self.max_size = max_size
       
        return MutatorBygj.array(test_case_code)
        
    def mutate_globalvar(self, test_case_code: str, max_size: int = 30) -> List[str]:

        self.max_size = max_size
       
        return MutatorBygj.globalvar(test_case_code)
    '''

    def mutate_typearr(self, test_case_code: str, max_size: int = 3) -> List[str]:

        self.max_size = max_size
        result = []
       
       
        for i in range(0,self.max_size):
            result.append(Mutate_array.recurarrdef(test_case_code))
        tem = set(result)
        result = list(tem)
        return result


       


    def mutate_longArrMethod(self, test_case_code: str, max_size: int = 3) -> List[str]:

        self.max_size = max_size
        result = []
        callable_proc = CallableProcessor("callables")
        result_type = callable_proc.generate_self_calling(test_case_code)
        if result_type != None:
            params_str = result_type[0]
           
            params = params_str.split(',')
           
            types = result_type[1]
           
            type2 = []
            num = 0
            for type1 in types:
                type2.append(len(type1))
                num = num + len(type1)
           
            if num == len(type2):
               
               
                for i in range(0,self.max_size):
                    result.append(Mutate_array.longarrmethod(test_case_code,types,params))
                if result[0] != "false":
                   
                    tem = set(result)
                    result = list(tem)
                    return result

       





class Mutator_regex:
    def __init__(self, engine: str = "node", max_size: int = 1):
        self.max_size = max_size 

    def mutate_regEx (self,test_case_code: str,max_size: int = 1)-> List[str]:
        testcase_list = []
        for num in range(self.max_size):
            testcase_list.append(Mutate_RegExp().generate_regExp(test_case_code))
        return testcase_list
