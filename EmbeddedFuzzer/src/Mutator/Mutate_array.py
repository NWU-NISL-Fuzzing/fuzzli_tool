import random
import sys
from typing import List

sys.path.extend(['../EmbeddedFuzzer', '../EmbeddedFuzzer/src'])
sys.path.extend(['../EmbeddedFuzzer/src/Postprocessor','../EmbeddedFuzzer/src/Mutator'])
from callable_type import CallableProcessor

class Mutate_Array:
    def __init__(self, max_size: int = 1):
        self.max_size = max_size 
    
    def arraymethod(self,testcase,params) -> str:
        lines = testcase.splitlines()
        if len(lines) >= 2:
            start = '\n'.join(lines[0:2])
            end = '\n'.join(lines[2:])

        typemu = "    //array method mutation"
        part1temp = "    var count=arr.length;\n    for (let i = 0; i < 100; i++) {\n        for (let j = 0; j <count ; j++) {\n            arr.push(arr[j]);\n        }\n    }"
        arrayop1 = "    arr.toString();"
        arrayop2 = "    arr.concat(\"1\");"
        arrayop3 = "    arr.toLocaleString();"
        arrayop4 = "    arr.join();"
        arrayop5 = "    arr.pop();"
        arrayop6 = "    arr.push(\"Kiwi\");"
        arrayop7 = "    arr.reverse();"
        arrayop8 = "    arr.shift();"
        arrayop9 = "    arr.slice(1, 3);"
        arrayop10 = "    arr.sort();"
        arrayop11 = "    arr.splice(2, 0, \"Lemon\", \"Kiwi\");"
        arrayop12 = "    arr.unshift(\"Lemon\",\"Pineapple\");"
        arrayop13 = "    arr.indexOf(\"Apple\");"
        arrayop14 = "    arr.lastIndexOf(\"Apple\");"
        arrayop15 = "    function checkAdult(age) {\n        return age >= 18;\n    }\n    function myFunction() {\n        document.getElementById(\"demo\").innerHTML = arr.every(checkAdult);\n    }"
        arrayop16 = "    function checkAdult(age) {\n        return age >= 18;\n    }\n    function myFunction() {\n        document.getElementById(\"demo\").innerHTML = arr.some(checkAdult);\n    }"
        arrayop17 = "    arr.forEach(myFunction);\n    function myFunction(item, index) {\n        document.getElementById(\"demo\").innerHTML += index + \":\" + item;\n    }"
        arrayop18 = "    arr.map(Math.sqrt)"
        arrayop19 = "    function checkAdult(age) {\n        return age >= 18;\n    }\n    function myFunction() {\n        document.getElementById(\"demo\").innerHTML = arr.filter(checkAdult);\n    }"
        arrayop20 = "    document.getElementById(\"demo\").innerHTML = arr.reduce(myFunc);\n    function myFunc(total, num) {\n        return total - num;\n    }"
        arrayop21 = "    document.getElementById(\"demo\").innerHTML = arr.reduceRight(myFunc);\n    function myFunc(total, num) {\n        return total - num;\n    }"
        arrayop22 = "    arr.valueOf();"
         
        arr1 = random.choice([arrayop1, arrayop2, arrayop3, arrayop4, arrayop5, arrayop6, arrayop7, arrayop8, arrayop9, arrayop10, arrayop11, arrayop12, arrayop13, arrayop14, arrayop15, arrayop16, arrayop17, arrayop18, arrayop19, arrayop20, arrayop21, arrayop22])
        result = start + '\n' +typemu
        param = random.choice(params)
        part1=part1temp.replace('arr', param)
        muarr = arr1.replace('arr', param)
        temp="    for (i = 0; i < 1e4; i++) {\n    "+arr1+"\n    }"
        part2=temp.replace('arr', param)
        result = result+'\n'+part1+'\n'+part2 + '\n' + end
        return result
    
    def mutateArray(self, test_case_code: str, max_size: int = 1) -> List[str]:
        self.max_size = max_size
        result = []
        callable_proc = CallableProcessor("callables")
        result_type = callable_proc.generate_self_calling(test_case_code)
        if result_type is not None:
            params_str = result_type[0]
            params = params_str.split(',')
            types = result_type[1]
            usefulParams=[]
            for index, type in enumerate(types):
                for onetype in type:
                    if(onetype=='array'):
                        usefulParams.append(params[index])
            if usefulParams:
                for i in range(0,self.max_size):
                    result.append(self.arraymethod(test_case_code,usefulParams))
                tem = set(result)
                result = list(tem)
                return result
            else:
                return []
        else:
            return []
        
if __name__ == "__main__":
    print(Mutate_Array().mutateArray("var NISLFuzzingFunc =\nfunction (assert,a) {\n    assert.indexOf();\n    a.length();\n};\nvar NISLParameter0 = [75796.050277646765378825, -236.7972288504747725, -369067.5470504556349562, 9.4621187615698641, 3031.0986789371608533, -1360226049.46538397598441383, -2.7347022056853749, 8443407293.1018703416315655, -321.7327071640735098, 134729258.36120453260173846, 76800.10444429954492884];\nvar NISLCallingResult = NISLFuzzingFunc(NISLParameter0);\nprint(NISLCallingResult);")[0])
    




































#     arrayop17 = "    arr.pop();"
#     arrayop18 = "    arr.push(\"Kiwi\");"
#     arrayop19 = "    document.getElementById(\"demo\").innerHTML = arr.reduce(myFunc);\n    function myFunc(total, num) {\n        return total - num;\n    }"
#     arrayop20 = "    document.getElementById(\"demo\").innerHTML = arr.reduceRight(myFunc);\n    function myFunc(total, num) {\n        return total - num;\n    }"
#     arrayop21 = "    arr.reverse();"
#     arrayop22 = "    arr.shift();"
#     arrayop23 = "    function checkAdult(age) {\n        return age >= 18;\n    }\n    function myFunction() {\n        document.getElementById(\"demo\").innerHTML = arr.every(checkAdult);\n    }"
#     arrayop24 = "    arr.slice(1, 3);"
#     arrayop25 = "    function checkAdult(age) {\n        return age >= 18;\n    }\n    function myFunction() {\n        document.getElementById(\"demo\").innerHTML = arr.some(checkAdult);\n    }"
#     arrayop26 = "    arr.sort();"
#     arrayop27 = "    arr.splice(2, 0, \"Lemon\", \"Kiwi\");"
#     arrayop28 = "    arr.toString();"
#     arrayop29 = "    arr.unshift(\"Lemon\",\"Pineapple\");"
#     arrayop30 = "    arr.valueOf();"
    
#     arr1 = random.choice([arrayop1, arrayop2, arrayop3, arrayop4, arrayop5, arrayop6, arrayop7, arrayop8, arrayop9, arrayop10, arrayop11, arrayop12, arrayop13, arrayop14, arrayop15, arrayop16, arrayop17, arrayop18, arrayop19, arrayop20, arrayop21, arrayop22, arrayop23, arrayop24, arrayop25, arrayop26, arrayop27, arrayop28, arrayop29, arrayop30])
#     result = start + '\n' +typemu
#     j = 0
#     z = 0
#     for vartype in types:
#         j = j+1
#         if vartype == ['array']:
#             z = z+1
#            
#             param = params[j-1]
#             part1 = part1temp.replace('arr', param)
#             muarr = arr1.replace('arr', param)
#             result = result+'\n'+part1+'\n'+muarr
#            

#     if z>0:
#         result = result + '\n' + end
#         return result
#     else:
#         return "false"

#
# def recurarrdef(testcase) -> str:
#    
#    
#     start1, _, end1 = testcase.partition('\n')
#     start2, _, end = end1.partition('\n')
#     start = start1+start2
#    
#     part2temp = str(re.findall(r'[(](.*?)[)]', start))
#     _, __, part2temp2 = part2temp.partition('\'')
#     part2, _, __ = part2temp2.partition('\'')

#    
#     start1, _, end1 = start.partition(')')
#    
#     typemu = "    //Recursively defining ultra long type array mutations"
#    
#     part1="\n    if(n==1){\n        return 0;\n    }"
    
#     start = start1+", n"+_+end1+"\n"+typemu+part1
#
#    
#    
#     def1 = "    var v0 = new Float64Array(1000000);"
#     def2 = "    var v0 = new Float32Array(1000000);"
#     def3 = "    var v0 = new Int8Array(1000000);"
#     def4 = "    var v0 = new Uint8Array(1000000);"
#     def5 = "    var v0 = new Uint8ClampedArray(1000000);"
#     def6 = "    var v0 = new Int16Array(1000000);"
#     def7 = "    var v0 = new Uint16Array(1000000);"
#     def8 = "    var v0 = new Int32Array(1000000);"
#     def9 = "    var v0 = new Uint32Array(1000000);"
#     def10 = "    var v0 = new BigInt64Array(1000000);"
#     def11 = "    var v0 = new BigUint64Array(1000000);"
#     def12 = "    var v0 = new ArrayBuffer(1000000);"
#     arr1 = random.choice([def1, def2, def3, def4, def5, def6, def7, def8, def9, def10, def11, def12])
#     part2 ="    NISLFuzzingFunc("+part2+", n-1);"
#     result = start + '\n' +arr1 + '\n' + part2

#     end1, _, end2 = end.rpartition('\n')
#     end1, _, end3 = end1.rpartition('\n')
#     part3 = "\nvar n = 10000;"

#    
#     part4, _, __ = end3.partition(')')
#     part4 = part4 + ", n);"
#     end = end1+part3+"\n"+part4+"\n"+end2

#     result = result + '\n' + end
#     return result