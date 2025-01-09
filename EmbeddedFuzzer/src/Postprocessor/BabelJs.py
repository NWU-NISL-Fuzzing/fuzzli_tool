import os
import subprocess
import sys

import tensorflow as tf

from db_operation import DBOperation


class BabelJS:
    def __init__(self, data_folder, dir_name, db_folder, remove_if_files_exist=True):
        self.data_folder = data_folder
        self.dir_name = dir_name
        self.db_folder = db_folder
        self.remove_if_files_exist = remove_if_files_exist

    def transform(self):
        source_path = self.data_folder + self.dir_name
        if not os.path.exists(source_path):
            print('Error: \'' + source_path + '\' is not exist! Check and do the last step again.')
            return False

        db_path = self.db_folder + '/BabelJs' + self.dir_name + ".db"
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
                    if self.syntax_transform(source_path + '/' + file):  
                        with open(source_path + '/' + file, 'r') as f:  
                            file_content = f.read().replace('var a = ', '', 1)  
                            contents.append([file_content.encode('utf-8')])
                db_op.insert(["Content"], contents)
            counter += 0
            print('\rExecute Last Filtration Finished on ' + str(counter) + ' Files')
            db_op.finalize()
            return True
        else:
            print('\'' + source_path + '\' Is Not A Directory.')
            return False

    def syntax_transform(self, file_path):

        cmd = ['babel', file_path, '-o', file_path]

        p = subprocess.Popen(cmd, stderr=subprocess.PIPE)
        
        
        if ((p.poll() is None) and p.stderr.readline() and os.path.exists(file_path)) or not os.path.getsize(
                file_path):
            return False
        return True


if __name__ == '__main__':
    FLAGS = tf.flags.FLAGS
    tf.flags.DEFINE_string('data_folder', '../../BrowserFuzzingData/FORYHY', 'Path of Data Folder')
    tf.flags.DEFINE_string('dir_name', 'FORYHYList1', 'Path of Corpus Folder')
    tf.flags.DEFINE_string('db_folder', '../../BrowserFuzzingData/db', 'Path of Corpus Folder')
    BabelTransform = BabelJS(FLAGS.data_folder, FLAGS.dir_name, FLAGS.db_folder)
    BabelTransform.transform()
