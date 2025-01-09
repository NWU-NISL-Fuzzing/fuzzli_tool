import random
from typing import List
import re
from typing import List


class Mutate_Object:
    def __init__(self, max_size: int = 1):
        self.max_size = max_size 
    
    def objectmethod(self,testcase,match) -> str:
        matched_content = match.group(1)  
        temp1="    for (NISLi = 0; NISLi < 16 - 1; NISLi++) {\n        obj['prop-' + NISLi] = 1;\n    }\n    obj['foo'] = 123;"
        part1=temp1.replace('obj', matched_content)
        
        
        obj1 = "void Object.getPrototypeOf(obj);"
        obj2 = "void Object.getOwnPropertyDescriptor(obj,'foo');"
        obj3 = "res = Object.create(obj);"
        obj4 = "var of = Object.freeze(obj);"
        obj5 = "var os = Object.seal(obj);"
        obj6 = "var odp = Object.defineProperties(obj,obj);"
        obj7 = "var odp = Object.defineProperty(obj,'a',obj);"
        obj8 = "void Object.getOwnPropertyNames(obj);"
        obj9 = "void Object.preventExtensions(obj);"
        obj10 = "void Object.isSealed(obj);"
        obj11 = "void Object.isFrozen(obj);"
        obj12 = "void Object.isExtensible(obj);"
        obj13 = "void Object.keys(obj);"
        obj14 = "void Object.toString();"
        obj15 = "void Object.toLocaleString();"
        obj16 = "void Object.valueOf();"
        obj17 = "void Object.hasOwnProperty();"
        obj18 = "void Object.isPrototypeOf();"
        obj19 = "void Object.propertyIsEnumerable();"


        objtemp = random.choice([obj1, obj2, obj3, obj4, obj5, obj6, obj7, obj8, obj9, obj10, obj11, obj12, obj13, obj14, obj15, obj16, obj17, obj18, obj19])
        temp2="    for (NISLi = 0; NISLi < 1e4; NISLi++) {\n        "+objtemp+"\n    }"
        part2=temp2.replace('obj', matched_content)

        typemu = "    //object method mutation"

        matched_end = match.end()  
        modified_text = testcase[:matched_end] + "\n" + part1 + "\n" + part2 + "\n" + typemu + testcase[matched_end:]
        
        return modified_text

    def mutateObject(self, testcase: str, max_size: int = 1) -> List[str]:
        self.max_size = max_size
        result = []
        object_pattern = r'(\w+)\s*=\s*{.*:.*};'
        match = re.search(object_pattern, testcase,re.DOTALL)
        if match:
            for i in range(0,self.max_size):
                result.append(self.objectmethod(testcase,match))
            tem = set(result)
            result = list(tem)
            return result
        return []           


if __name__ == "__main__":
    print(Mutate_Object().mutateObject("var NISLFuzzingFunc = \nfunction(d) {\n    object1 = {\n        macro: d[0],\n        args: d[2],\n        exprs: d[8]\n    };\n}\n;\nvar NISLParameter0 = [\"z? wY!duOk>b}27\"hx@sOqtQc\",c|U()(O,#bBdS&[TS{oI2&pfKd%bnL=Q=wp-Nq3Eg0XIQi,|JRH-7*JK?=R2prs|O@)8gEkU(TB+r*p{j:%f.r8fT{H\", \"6v/$}_hPwks=)+|<(lU.d=aQcE|:WC|':[\", \"49\"Wj2[roO+>j_RF)Ha)V\\No3,f&8zcD3;CG*N8=6SmDY$`m$FfI(z#BZk+<yR4H,#3[fuMR6-UFzfe2ObR\", \"9xve\">@JmK3VC'<xtdrDVT}=Rct&K3Uf~nl*!x#:G16VjbO?GM{_a.:2x={Bo^r^<?H'6Rc,6%9NIx\", \"O(Smx#0Bf+4BNo78_X5T-m(.;xhVWk)'d~4ohA8@BK~7{mGishPW+d,!oJCbW!o'~>E+hA\">:eUVGs)vAt=-e1J+rwj*!j>v)0PFnD,QL;/E9d\"];\nvar NISLCallingResult = NISLFuzzingFunc(NISLParameter0);\nprint(NISLCallingResult);")[0])
    
    










