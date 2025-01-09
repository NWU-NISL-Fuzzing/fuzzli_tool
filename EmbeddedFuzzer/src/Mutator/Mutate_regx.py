import random
import re
from random import choice
from typing import List

from xeger import Xeger






list_rege = ['\\\d','\\\D','\\\w','\\\W','\\\s','\\\S','\\\b','\\\B','\\\f','\\\n','\\\r','\\\t','\\\v','^','$','\\\\','.','|']

list_limit = ['+','?','*']

list_Modifier = ['i','g','m']
list_limit_number = ['{n}','{n,}','{n,m}']


def generateChr():
    
    temp = '{0:x} {1:x}'.format(random.randint(0xb0, 0xf7), random.randint(0xa1, 0xf9))
    chr = bytes.fromhex(temp).decode('gb2312')
    return chr

class GenerateStr(object):
    def __init__(self, category, num, length=10):
        self.length = length
        self._cateory = category
        self.num = num
        self._categories = {
            "pure_num": r'[0-9]{%d}' % self.length,
            "pure_alph": r'[a-zA-Z]{%d}' % self.length,
            "num_alph": r'[a-zA-Z0-9]{%d}' % self.length,
            "pure_chr": r'[%s]{%d}' % (generateChr(), self.length),
            "num_chr": r'[0-9%s]{%d}' % (generateChr(), self.length),
            "alph_chr": r'[a-zA-Z%s]{%d}' % (generateChr(), self.length),
            "num_alph_chr": r'[a-zA-Z0-9%s]{%d}' % (generateChr(), self.length)
        }

    def _chooseCategory(self):
        try:
            choose_category = self._categories[self._cateory]
        except KeyError:
            print("sorry,the input is uncorrect!")
            choose_category = r'please rewrite the category'
        return choose_category

    def _generateStr(self):

        gen_str = [0 for _ in range(self.num)]
        str_xeger = Xeger(limit=10)
        str = self._chooseCategory()

        for i in range(0, self.num):
            gen_str[i] = str_xeger.xeger(str)
            
        return gen_str

    def getStr(self):
        result = self._generateStr()
        return result


class Mutate_RegExp:
    def __init__(self,length=10):
        self.length = length

    def main(self):
        try:
            
            self.generate_rege()
        except BaseException as e:
            raise e

    
    def assemble_rege(self,str_rege):
        list_rege = []

        index_number = random.randint(0,100)
        do_con = '\tvar index = '+str(index_number)+';\n'
        do_con2 = '\tdo{\n'+'\n'+'\t\tindex++;\n'
        js_rege1 = '\t\tvar re = /'+str_rege+'/'+random.choice(list_Modifier)+';\n'
        do_con3 = '\t} while(index<'+str(random.randint(1000,100000))+');\n'



        
        
        list_regx_op = ['exec','test']
        x = GenerateStr('num_alph', 5, 10)
        js_rege2 = '\t\tvar myArray = re.'+random.choice(list_regx_op)+'("'+str(random.choice(x.getStr()))+'")'+';\n'
        js_rege3 = '\t\tprint("The value of myArray is " + myArray);\n'
        
        list_rege.append(do_con)
        list_rege.append(do_con2)
        list_rege.append(js_rege1)
        list_rege.append(js_rege2)
        list_rege.append(js_rege3)
        list_rege.append(do_con3)
        list_rege.append("\t//mutate by regExp\n")

        return list_rege

    def generate_regExp(self,original_test_case):
        
        x = GenerateStr('num_alph', 5, 50)  
        
        str_rege = choice(list_rege)+str(random.choice(x.getStr()))+str(random.choice(list_limit))
        rege_list = self.assemble_rege(str_rege)
        index = str(original_test_case).count('var NISLFuzzingFunc = ')
        
        content = original_test_case.split("\n")

        for i in rege_list:
            content.insert(index+2, str(i))
            index = index + 1
        return "\n".join(content)
                    
    


    def regexmethod(self, testcase) -> str:
        regex_pattern = r'(?<!/)/(?!/)[^\s<>]*(?<!/)/(?!/)[gimyu]{0,5}'
        match = re.search(regex_pattern, testcase)
        
        if match is None:
            return ""
        x = GenerateStr('num_alph', 5, random.randint(1, 100))

        
        str_rege = str(random.choice(x.getStr())) + str(random.choice(list_rege)) + str(random.choice(list_limit))   

        js_rege1 = '/'+str_rege+'/'+random.choice(list_Modifier)
        
        try:
            typemu = "\n    //regex method mutation\n"
            lines = testcase.splitlines()
            if len(lines) >= 2:
                start = '\n'.join(lines[0:2])
                end = '\n'.join(lines[2:])
            testcase = start + typemu+ end
            newtextcase = re.sub(regex_pattern, str(js_rege1), testcase)
        except Exception as e:
            print(e)
            return ""
        return newtextcase

    def mutateRegex(self, test_case_code: str, length: int = 1) -> List[str]:
        self.length = length
        result = []
        
        testcase=self.regexmethod(test_case_code)
        if testcase!="":
            result.append(testcase)
        return result


if __name__ == "__main__":
    print(Mutate_RegExp().mutateRegex('var NISLFuzzingFunc = \nfunction(label) {\n    return label.toLowerCase().replace(/^\s+|\s+$/g, "").replace(/\W+/g, "-");\n}\n;\nvar NISLParameter0 = "&%iR!|Ij";\nvar NISLCallingResult = NISLFuzzingFunc(NISLParameter0);\nprint(NISLCallingResult);')[0])


















# function() {
    
#         var index = 97;

#         do{

#                 index++;

#                 var re = /$1TELTje8NV0BmiY7RDLxqik5AAmcq6DQFLNmAL25GifNDDBd3NqjuC9yTcngGiJmAGMDY4NEAj1SNNnkVd4T0UDZI3xikRmPepqr?/m;

#                 var myArray = re.test("CCjQsszitw");

#                 print("The value of myArray is " + myArray);

#         } while(index<37073);

#         //mutate by regExp

# return this.caboose === true;
# }
# ;
# var NISLCallingResult = NISLFuzzingFunc();
# print(NISLCallingResult);