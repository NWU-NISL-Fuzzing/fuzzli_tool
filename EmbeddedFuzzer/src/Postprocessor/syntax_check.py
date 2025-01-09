import os
import re
import subprocess


def file_split(file_path):

    
    with open(file_path, 'r', encoding='utf-8') as RawFile:
        content = RawFile.read()
        list = re.split('-------------------------------------', content)

    
    js_list = [("var a = " + i).strip().replace('\n', '') for i in list]

    return js_list


def syntax_check(file_path):

    cmd = ['uglifyjs', file_path, '-o', file_path]

    
    
    p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
    if ((p.poll() is None) and p.stderr.readline().__len__() > 0 and os.path.exists(file_path)) or not os.path.getsize(
            file_path):
        return False
    return True


if __name__ == "__main__":

    
    file_path = './FORYHY/FORYHYList1/'   
    count = 0
    

    right = 0
    false = 0

    for root, dirs, files in os.walk(file_path):
        for file in files:
            if count % 50 == 0:
                print("Now process:",count)
            if syntax_check(file_path + file):
                right += 1
                print(count)
            else:
                false += 1
            count += 1

    print('right:' + str(right))
    print('false:' + str(false))


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
