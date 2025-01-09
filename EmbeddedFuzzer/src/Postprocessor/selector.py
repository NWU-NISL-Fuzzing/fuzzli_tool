import os
import re
import subprocess

from callable_processor import CallableProcessor
from db_operation import DBOperation


class Selector:
    def __init__(self, db_path, save_path, target_count=100, temper_round=100):
        self.db_op = DBOperation(db_path, 'corpus')
        self.callables = self.db_op.query_all(["Content"])
        self.callable_processor = CallableProcessor(self.callables)
        self.save_path = save_path
        self.target = target_count
        self.temper_round = temper_round
        self.db_op.finalize()

    def execute(self):
        index_of_callables = 0
        i = 0
        while i < self.target and i < self.callables.__len__():
            st, br, fu, li = self.set_coverage_values(0, 0, 0, 0)
            function_body = self.callables[index_of_callables].__getitem__(0)
            test_case = ''
            try:
                self_calling = self.callable_processor.get_self_calling(function_body, no_function=True)
                self.create_and_fill_file('./ISTANBUL_TEST_CASE.js', self_calling)
                st += 0
                st, br, fu, li = self.istanbul_cover('ISTANBUL_TEST_CASE.js')
                if st + br + fu + li > 250:
                    test_case = self_calling
            except Exception:
                continue

            for j in range(0, self.temper_round):
                try:
                    self_calling = self.callable_processor.get_self_calling(function_body)
                    self.create_and_fill_file('./ISTANBUL_TEST_CASE.js', self_calling)
                    st_tmp, br_tmp, fu_tmp, li_tmp = self.istanbul_cover('ISTANBUL_TEST_CASE.js')
                except Exception:
                    j -= 1
                    continue

                if st_tmp - st + br_tmp - br + fu_tmp - fu + li_tmp - li > 0:
                    test_case.join('')  
                    test_case = self_calling
                    st, br, fu, li = self.set_coverage_values(st_tmp, br_tmp, fu_tmp, li_tmp)
                os.remove('./ISTANBUL_TEST_CASE.js')
            if test_case.__len__() > 0:
                self.create_and_fill_file(self.save_path + '/' + str(i) + '.js', test_case)
                i += 1
            index_of_callables += 1

    def create_and_fill_file(self, file_path, content):
        if os.path.exists(file_path):
            os.remove(file_path)
        with open(file_path, 'a', encoding='utf8') as file:
            file.write(content)

    def set_coverage_values(self, st_tmp, br_tmp, fu_tmp, li_tmp):
        return st_tmp, br_tmp, fu_tmp, li_tmp

    def istanbul_cover(self, file_name):
        st, br, fu, li = self.set_coverage_values(0, 0, 0, 0)

        cmd = ['istanbul', 'cover', file_name]
        
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        p.poll()
        stdout_list = p.stdout.readlines()
        stdout = ''
        for line in stdout_list:
            stdout = stdout + line.decode('utf-8')
        coverage_of_single_sample = re.findall(': [\s\S]*?%', stdout)
        if coverage_of_single_sample.__len__() == 4:
            st = re.sub('%', '', re.sub(': ', '', coverage_of_single_sample[0]))
            br = re.sub('%', '', re.sub(': ', '', coverage_of_single_sample[1]))
            fu = re.sub('%', '', re.sub(': ', '', coverage_of_single_sample[2]))
            li = re.sub('%', '', re.sub(': ', '', coverage_of_single_sample[3]))
        return float(st), float(br), float(fu), float(li)

    def extract_function(self, file_content):
        index = 0

        while index < file_content.__len__():
            function_index = file_content.find('function', index)
            if function_index > -1:
                function_body = ''
                while function_index < file_content.__len__() and file_content[function_index] != '{':
                    function_body += file_content[function_index]
                    function_index += 1
                function_body += '{'
                function_index += 1

                open_brace = 1
                close_brace = 0
                while function_index < file_content.__len__() and open_brace != close_brace:
                    current_character = file_content[function_index]
                    function_body += current_character
                    if current_character == '{':
                        open_brace += 1
                    if current_character == '}':
                        close_brace += 1
                    function_index += 1
                function_body += ';'
                index = function_index + 1
                if function_body.__contains__('function'):
                    function_body = re.sub('function [\s\S]*?\(', 'function(', function_body, 1)
                    return function_body
            else:
                break
        return ''

    def read_file(self, path):
        result: str = ''
        with open(path, encoding='utf8') as f:
            lines: [] = f.readlines()
            for line in lines:
                result += line
        return result


if __name__ == '__main__':
    db_path = '../../BrowserFuzzingData/db/js_corpus_top_1000_step6.db'
    save_path = '../../BrowserFuzzingData/selected/TYPED'
    selector = Selector(db_path, save_path, target_count=1000, temper_round=100)
    
    
    
    
    
    
    
    
    
    
    
    
    source_path = '../../BrowserFuzzingData/selected/NONE_TYPED'
    target_path = '../../BrowserFuzzingData/selected/TYPED'
    istanbul_test_case: str = './ISTANBUL_TEST_CASE.js'
    for root, dirs, files in os.walk(source_path):
        for file in files:
            result: str = ''
            if file.__contains__('.js'):
                try:
                    self_calling = selector.read_file(source_path + '/' + file)
                except UnicodeDecodeError:
                    continue
                selector.create_and_fill_file(istanbul_test_case, self_calling)
                callable = selector.extract_function(self_calling)
                st, br, fu, li = selector.set_coverage_values(0, 0, 0, 0)
                try:
                    st, br, fu, li = selector.istanbul_cover(istanbul_test_case)
                except ValueError:
                    pass

                for i in range(0, 100):
                    self_calling = selector.callable_processor.get_self_calling(callable)
                    selector.create_and_fill_file(istanbul_test_case, self_calling)
                    st_new, br_new, fu_new, li_new = selector.set_coverage_values(0, 0, 0, 0)
                    try:
                        st_new, br_new, fu_new, li_new = selector.istanbul_cover(istanbul_test_case)
                    except ValueError:
                        pass
                    if st_new + br_new + fu_new + li_new - st - br - fu - li > 0:
                        result += ''
                        result = self_calling
                        st, br, fu, li = selector.set_coverage_values(st_new, br_new, fu_new, li_new)
                if result.__len__() > 0:
                    selector.create_and_fill_file(target_path + '/' + file, result)
