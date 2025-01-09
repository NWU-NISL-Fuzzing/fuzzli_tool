#coding=utf-8
import sqlite3

def getFunction():
    result = []
    result_norequire = []
    with open('/home/Comfort_all/data/datasets/train1.txt', 'r') as f:
        str1 = f.read()
        result = str1.split('<|endoftext|>')

    for i in result:
        if i.count('require')==0:
            result_norequire.append(str(i))
    return result_norequire
    
def saveTodb(result_norequire):
    conn = sqlite3.connect('top2000corpus-20230106-FX-SF.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS Corpus(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    simple BLOB NOT NULL,
    used INTEGER default 0,
    UNIQUE(simple)
    );
''')
    print ("Table created successfully")
    for simple in result_norequire:
        if len(simple) !=0:
            sql = "INSERT OR IGNORE INTO Corpus (simple) VALUES (?)"
            conn.execute(sql,[simple])
    conn.commit()

if __name__ == '__main__':
    saveTodb(getFunction())
