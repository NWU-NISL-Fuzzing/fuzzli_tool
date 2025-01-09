
import os
import re
import subprocess
import sys
import uuid

import tensorflow as tf

from db_operation import DBOperation


class PostProcessor:
    def __init__(self, data_folder, raw_folder, db_folder, format=True, compress=False, mangle=False,
                 do_syntax_transform=False, remove_if_files_exist=True):
        self.data_folder = data_folder
        self.raw_folder = raw_folder
        self.db_folder = db_folder
        self.job_name = self.get_job_name()
        self.format = format
        self.compress = False if self.format else compress
        self.mangle = mangle
        self.do_syntax_transform = do_syntax_transform
        self.remove_if_files_exist = remove_if_files_exist

    def get_job_name(self):
        tmp = self.raw_folder.split('/')
        return tmp.__getitem__(tmp.__len__() - 1)

    def generate_pure_correct_callables(self):
        print('Step 1 --> Initial Filtration: ')
        if not self.initial_filtration():
            return

        print('Step 2 --> Write Files to DB: ')
        if not self.write_files_to_db():
            return

        print('Step 3 --> Functionize: ')
        if not self.functionize():
            return

        print('Step 4 --> Redistribute: ')
        if not self.redistribute():
            return

        print('Step 5 --> Last Filtration: ')
        if not self.last_filtration():
            return

        print('Step 6 --> Final Distinct: ')
        if not self.final_distinct():
            return

    def initial_filtration(self):


        counter = 0
        illegal_counter = 0
        if os.path.exists(self.raw_folder) and os.path.isdir(self.raw_folder):
            for root, dirs, files in os.walk(self.raw_folder):
                
                for file in files:
                    counter += 1
                    progress = "\rProcessing: %d --> %s" % (counter, file)
                    sys.stdout.write(progress)
                    file_path = self.raw_folder + '/' + file
                    if not self.syntax_check(file_path):
                        illegal_counter += 1
                        os.remove(file_path)
            counter += 0
            print('\rExecute Initial Filtration Finished on ' + str(counter) + ' Raw Files.')
            print(str(illegal_counter) + ' Illegal Ones Has Been Removed.')
            return True
        else:
            print('\'' + self.raw_folder + '\' Is Not A Directory.')
            return False

    def write_files_to_db(self):
        corpus_path = self.raw_folder
        
        if not os.path.exists(corpus_path):
            print('Error: \'' + corpus_path + '\' is not exist! Check and do the last step again.')
            return False

        
        db_path = self.db_folder + '/js_corpus_' + self.job_name + '_step2.db'
        db_op = DBOperation(db_path, 'corpus')
        if self.remove_if_files_exist:
            if os.path.exists(db_path):
                os.remove(db_path)
            db_op.init_db()
        elif not os.path.exists(db_path):
            db_op.init_db()

        counter = 0
        if os.path.isdir(corpus_path):
            for root, dirs, files in os.walk(corpus_path):
                
                contents = []
                for file in files:
                    try:
                        counter += 1
                        progress = "\rProcessing: %d --> %s" % (counter, file)
                        sys.stdout.write(progress)
                        f = open(corpus_path + '/' + file, 'rb')
                        contents.append([f.read().decode()])
                        f.close()
                    except Exception:
                        pass
                db_op.insert(["Content"], contents)
            counter += 0
            print('\rExecute Writing Content to DB Finished on ' + str(counter) + ' Files.')
            db_op.finalize()
            return True
        else:
            print('\'' + corpus_path + '\' Is Not A Directory.')
            return False

    def functionize(self):
        source_db_path = self.db_folder + '/js_corpus_' + self.job_name + '_step2.db'
        if not os.path.exists(source_db_path):
            print('Error: \'' + source_db_path + '\' is not exist! Check and do the last step again.')
            return False

        target_db_path = self.db_folder + '/js_corpus_' + self.job_name + '_step3.db'
        source_db_op = DBOperation(source_db_path, 'corpus')
        target_db_op = DBOperation(target_db_path, 'corpus')
        if self.remove_if_files_exist:
            if os.path.exists(target_db_path):
                os.remove(target_db_path)
            target_db_op.init_db()
        elif not os.path.exists(target_db_path):
            target_db_op.init_db()

        raws = source_db_op.query_all(["Content"])

        counter = 0
        contents = []
        for raw in raws:
            counter += 1
            progress = "\rProcessing Raw No.%d" % counter
            sys.stdout.write(progress)
            raw = raw.__getitem__(0)
            if raw.__contains__('function'):
                self.extract_function(raw, contents)
        target_db_op.insert(["Content"], contents)
        target_size = target_db_op.query_count().__getitem__(0)
        counter += 0
        print('\rExecute Functionizing Finished. Extracted ' + str(target_size) + ' Functions From ' + str(
            counter) + ' Raws.')
        source_db_op.finalize()
        target_db_op.finalize()
        return True

    def redistribute(self):
        db_path = self.db_folder + '/js_corpus_' + self.job_name + '_step3.db'
        if not os.path.exists(db_path):
            print('Error: \'' + db_path + '\' is not exist! Check and do the last step again.')
            return False

        db_op = DBOperation(db_path, "corpus")
        callables = db_op.query_all(["Content"])
        target_path = self.data_folder + '/js_corpus_' + self.job_name + '_step4'
        if self.remove_if_files_exist:
            if os.path.exists(target_path):
                os.removedirs(target_path)
            os.mkdir(target_path)
        elif not os.path.exists(target_path):
            os.mkdir(target_path)

        counter = 0
        for callable in callables:
            counter += 1
            progress = "\rProcessing: %d" % counter
            sys.stdout.write(progress)
            content = callable.__getitem__(0).decode('utf-8')
            if re.findall('function[\s\S]*?\(', content).__len__() > 0:
                re.sub('function[\s\S]*?\(', 'function(', content, 1)
            content = 'var a = ' + content
            file_name = uuid.uuid4().__str__() + '.js'
            try:
                self.create_file(target_path + '/' + file_name, content)
            except Exception:
                pass
        counter += 0
        print('\rExecute Redistribution Finished on ' + str(counter) + ' Files')
        db_op.finalize()
        return True

    def last_filtration(self):
        source_path = self.data_folder + '/js_corpus_' + self.job_name + '_step4'
        if not os.path.exists(source_path):
            print('Error: \'' + source_path + '\' is not exist! Check and do the last step again.')
            return False

        db_path = self.db_folder + '/js_corpus_' + self.job_name + '_step5.db'
        db_op = DBOperation(db_path, "corpus")
        if self.remove_if_files_exist:
            if os.path.exists(db_path):
                os.remove(db_path)
            db_op.init_db()
        elif not os.path.exists(db_path):
            db_op.init_db()

        counter = 0
        if os.path.isdir(source_path):
            for root, dirs, files in os.walk(source_path):
                contents = []
                for file in files:
                    counter += 1
                    progress = "\rProcessing: %d --> %s" % (counter, file)
                    sys.stdout.write(progress)
                    if self.syntax_check(source_path + '/' + file):
                        if not self.do_syntax_transform or self.syntax_transform(source_path + '/' + file):  
                            with open(source_path + '/' + file, 'r') as f:  
                                file_content = f.read().replace('var a = ', '', 1)  
                                if file_content.__contains__('console.log'):  
                                    file_content = file_content.replace('console.log', 'print')
                                contents.append([file_content.encode('utf-8')])
                db_op.insert(["Content"], contents)
            counter += 0
            print('\rExecute Last Filtration Finished on ' + str(counter) + ' Files')
            db_op.finalize()
            return True
        else:
            print('\'' + source_path + '\' Is Not A Directory.')
            return False

    def final_distinct(self):
        source_db_path = self.db_folder + '/js_corpus_' + self.job_name + '_step5.db'
        if not os.path.exists(source_db_path):
            print('Error: \'' + source_db_path + '\' is not exist! Check and do the last step again.')
            return False

        target_db_path = self.db_folder + '/js_corpus_' + self.job_name + '_step6.db'
        source_db_op = DBOperation(source_db_path, 'corpus')
        target_db_op = DBOperation(target_db_path, 'corpus')
        if self.remove_if_files_exist:
            if os.path.exists(target_db_path):
                os.remove(target_db_path)
            target_db_op.init_db()
        elif not os.path.exists(target_db_path):
            target_db_op.init_db()

        counter = 1
        callbales = source_db_op.query_all(["Content"])
        distincted = set(callbales)  
        contents = []
        for callbale in distincted:
            progress = "\rProcessing: %d" % counter
            sys.stdout.write(progress)
            contents.append([callbale[0].decode('utf-8')])
            counter += 1
        target_db_op.insert(["Content"], contents)
        print('\rExecute Final Distinct Finished on ' + str(counter) + ' Files')
        source_db_op.finalize()
        target_db_op.finalize()
        return True

    def syntax_transform(self, file_path):

        cmd = ['babel', file_path, '-o', file_path]

        p = subprocess.Popen(cmd, stderr=subprocess.PIPE)
        
        
        if ((p.poll() is None) and p.stderr.readline() and os.path.exists(file_path)) or not os.path.getsize(
                file_path):
            return False
        return True

    def syntax_check(self, file_path):

        cmd = ['uglifyjs', file_path, '-o', file_path]
        if self.format:
            cmd.append('-b')
        elif self.compress:
            cmd.append('-c')
        if self.mangle:
            cmd.append('-m')

        p = subprocess.Popen(cmd, stderr=subprocess.PIPE)
        
        
        if ((p.poll() is None) and p.stderr.readline() and os.path.exists(file_path)) or not os.path.getsize(
                file_path):  
            return False
        return True

    def extract_function(self, file_content, contents: list):
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
                    contents.append([function_body.encode()])
            else:
                break

    def create_file(self, filename, file_content):
        file = open(filename, 'a')
        file.write(file_content)
        file.close()


if __name__ == '__main__':
    FLAGS = tf.flags.FLAGS
    tf.flags.DEFINE_string('file_type', 'js', 'File type of current execution.')
    tf.flags.DEFINE_string('data_folder', '../../BrowserFuzzingData', 'Path of Data Folder')
    tf.flags.DEFINE_string('raw_folder', '../../BrowserFuzzingData/1001_2000/js', 'Path of Corpus Folder')
    tf.flags.DEFINE_string('db_folder', '../../BrowserFuzzingData/db', 'Path of Corpus Folder')
    post_processor = PostProcessor(FLAGS.data_folder, FLAGS.raw_folder, FLAGS.db_folder)
    post_processor.generate_pure_correct_callables()
