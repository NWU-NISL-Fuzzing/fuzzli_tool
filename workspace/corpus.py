import os
import sqlite3

db_path="/home/workspace/top2000corpus-20250102.db"
def getCorpus():
    output_folder = '/home/20240222/corpus/yuan'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    conn = sqlite3.connect('/home/workspace/top2000corpus-20230106-FX-SF.db')
    cursor = conn.cursor()
    cursor.execute("select sample from Corpus")
    rows = cursor.fetchall()
    for idx, row in enumerate(rows):
        file_path = os.path.join(output_folder, f'data_{idx}.js')
        with open(file_path, 'w') as file:
            file.write(str(row[0]))
    conn.close()

def saveCorpus():
    conn = sqlite3.connect('/home/20240222/corpus/corpus-20240223.db')
    cursor = conn.cursor()

    for filename in os.listdir('/home/20240222/corpus/yuan'):
        file_path = os.path.join('/home/20240222/corpus/yuan', filename)

        with open(file_path, 'r') as file:
            file_content = file.read()

        cursor.execute(f'''
            INSERT INTO Corpus (sample)
            VALUES (?)
        ''', (file_content,))
    conn.commit()
    conn.close()

def dbCorpus():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("ALTER TABLE corpus ADD COLUMN flag BLOB")
    cursor.execute("UPDATE corpus SET flag = 0;")
    conn.commit()

    conn.close()

def flagTest():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    mydata = 0b11111
    string_data = bin(mydata)[2:] 
    #print(string_data)
    id_to_update = 1 
    conn.execute("UPDATE corpus SET flag = ? WHERE id = ?", [string_data, id_to_update])

    conn.commit()
    conn.close()


if __name__ == '__main__':
    flagTest()

