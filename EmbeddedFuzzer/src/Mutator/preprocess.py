




import re
import sqlite3
import sys
from typing import List

sys.path.extend(['../EmbeddedFuzzer', '../EmbeddedFuzzer/src'])
sys.path.extend(['../EmbeddedFuzzer/src/Postprocessor','../EmbeddedFuzzer/src/Mutator'])
from callable_type import CallableProcessor



def getparams(test_case_code: str) -> [List[str], List[str]]:
    callable_proc = CallableProcessor("callables")
    result_type = callable_proc.generate_self_calling(test_case_code)
    
    
    
        
    if result_type is not None:
        params_str = result_type[0]
        
        params = params_str.split(',')
        
        types = result_type[1]
        return params, types
    else:
        return None


def getnumber(testcase: str) -> str:
    
    binary_number = 0b00000
    
    if getparams(testcase) is not None:
        params, types=getparams(testcase)
        
        for type in types:
            for onetype in type:
                
                if binary_number & 0b01000 !=0b01000:
                    if(onetype=='array'):
                        binary_number = binary_number | 0b01000
                        
                if binary_number & 0b00010 !=0b00010:
                    if(onetype=='string'):
                        binary_number = binary_number | 0b00010
                        
    
    binary_number = binary_number | 0b10000

    
    
    
    
    
    regex_pattern = r'(?<!/)/(?!/)[^\s<>]*(?<!/)/(?!/)[gimyu]{0,5}'
    match = re.search(regex_pattern, testcase)
    if binary_number & 0b00100 !=0b00100:
        if match:
            
            binary_number = binary_number | 0b00100
            
            
            
            
            
    
    if binary_number & 0b00100 !=0b00100:
        pattern = r'RegExp|Regex|regex|exec\(|test\(|compile\(|match\(|search\('
        match = re.search(pattern, testcase)
        
        if match:
            
            binary_number = binary_number | 0b00100
            
            

    
    if binary_number & 0b00001 !=0b00001:
        
        
        object_pattern = r'(\w+)\s*=\s*{.*:.*};'
        match = re.search(object_pattern, testcase,re.DOTALL)
        if match:
            binary_number = binary_number | 0b00001
            
            
    if binary_number & 0b00001 !=0b00001:
        pattern = r'Object|object|keys\('
        match = re.search(pattern, testcase)
        
        if match:
            binary_number = binary_number | 0b00001
            
            
    
    
    return format(binary_number, '0{}b'.format(5))


def saveNumber(testcase: str):
    string_data=getnumber(testcase)
    
    
    
    conn = sqlite3.connect('../EmbeddedFuzzer/xxx/corpus-20240223.db')
    cursor = conn.cursor()
    conn.execute("UPDATE corpus SET flag = ? WHERE simple = ?", [string_data, testcase])
    
    conn.commit()
    
    conn.close()


def save():
    conn = sqlite3.connect('../EmbeddedFuzzer/xxx/corpus-20240223.db')
    cursor = conn.cursor()

    
    cursor.execute("SELECT simple FROM corpus where flag=0")
    rows = cursor.fetchall()

    
    simple_data_list = []

    
    for row in rows:
        simple_data = row[0]  
        simple_data_list.append(simple_data)  

    
    count = 0  
    for i, data in enumerate(simple_data_list, start=1):
        saveNumber(data)
        count += 1  
        if count % 1000 == 0:  
            print(f"Processed {count} records.")

   
   
   
   

   
    conn.close()


def saveTest():
    conn = sqlite3.connect('../EmbeddedFuzzer/xxx/corpus-20240223.db')
   
    cursor = conn.cursor()
    cursor.execute("SELECT simple FROM corpus")
    rows = cursor.fetchall()
    simple_data_list = []
    for row in rows:
        simple_data = row[0]
        simple_data_list.append(simple_data)
    count = 0
    for i, data in enumerate(simple_data_list, start=1):
        getnumber(data)
        count += 1
        if count % 1000 == 0: 
            print(f"Processed {count} records.")
    conn.close()

if __name__ == "__main__":
    save()
   
   
   
   
   
   
   
   
   
