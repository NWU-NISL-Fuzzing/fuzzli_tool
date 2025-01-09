import random
from typing import List



from callable_type import CallableProcessor


class Mutate_String:
    def __init__(self, max_size: int = 1):
        self.max_size = max_size 
    
    def stringmethod(self,testcase,params) -> str:
        lines = testcase.splitlines()
        if len(lines) >= 2:
            start = '\n'.join(lines[0:2])
            end = '\n'.join(lines[2:])

        typemu = "    //string method mutation"

        part1temp = "    while (sttr.length < 1e4) {\n        sttr = sttr + sttr;\n    }"
        
        arrayop1 = "    sttr.toString();"
        arrayop2 = "    sttr.valueOf();"
        arrayop3 = "    sttr.charAt(sttr.length-1);"
        arrayop4 = "    sttr.charCodeAt(sttr.length-1);"
        arrayop5 = "    sttr.toLocaleUpperCase();"
        arrayop6 = "    sttr.slice(0, sttr.length-1);"
        arrayop7 = "    sttr.substring(0, sttr.length-1);"
        arrayop8 = "    sttr.toLocaleLowerCase();"
        arrayop9 = "    sttr.toUpperCase();"
        arrayop10 = "    sttr.toLowerCase();"
        arrayop11 = "    str1=\"hello\";\nsttr.concat(\" \", str1);"
        arrayop12 = "    sttr.trim();"
        arrayop13 = "    sttr.replace(\"a\", \"b\");"
        arrayop14 = "    sttr.split(\" \")"
        arrayop15 = "    sttr.indexOf(\"a\");"
        arrayop16 = "    sttr.lastIndexOf(\"a\");"
        arrayop17 = "    sttr.localeCompare(\"a\");"
        arrayop18 = "    sttr.search(\"a\");"
        arrayop19 = "    sttr.match(\"a\");"
        
        arr1 = random.choice([arrayop1, arrayop2, arrayop3, arrayop4, arrayop5, arrayop6, arrayop7, arrayop8, arrayop9, arrayop10, arrayop11, arrayop12, arrayop13, arrayop14, arrayop15, arrayop16, arrayop17, arrayop18, arrayop19])
        result = start + '\n' +typemu

        param = random.choice(params)
        part1=part1temp.replace('sttr', param)
        muarr = arr1.replace('sttr', param)
        temp="    for (NISLi = 0; NISLi < 1e4; NISLi++) {\n    "+muarr+"\n    }"
        result = result+'\n'+part1+'\n'+temp + '\n' + end
        return result

    def mutateString(self, test_case_code: str, max_size: int = 1) -> List[str]:
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
                    
                    if(onetype=='string'):
                        usefulParams.append(params[index])
            if usefulParams:
                for i in range(0,self.max_size):
                    result.append(self.stringmethod(test_case_code,usefulParams))
                tem = set(result)
                result = list(tem)
                return result
            else:
                return []
        else:
            return []
        


if __name__ == "__main__":
    print(Mutate_String().mutateString("var NISLFuzzingFunc =\nfunction (assert,a) {\n    assert.indexOf();\n    a.length();\n};\nvar NISLParameter0 = [75796.050277646765378825, -236.7972288504747725, -369067.5470504556349562, 9.4621187615698641, 3031.0986789371608533, -1360226049.46538397598441383, -2.7347022056853749, 8443407293.1018703416315655, -321.7327071640735098, 134729258.36120453260173846, 76800.10444429954492884];\nvar NISLCallingResult = NISLFuzzingFunc(NISLParameter0);\nprint(NISLCallingResult);")[0])



