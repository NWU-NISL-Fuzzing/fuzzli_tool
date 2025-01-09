#coding=utf-8
import sqlite3

def get():
    conn = sqlite3.connect('top2000corpus-20200410-FX-SF.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS Corpus_4(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    simple BLOB NOT NULL,
    used INTEGER default 0,

    UNIQUE(simple)
    );
''')
    print ("Table created successfully")
    simples = conn.execute("select simple from Corpus limit 15000,5000")
    list1 = list(list(items) for items in list(simples))  
    # print(list1)
    print ("Records created successfully")
    index = 1
    for simple in list1 :
        simple1 = simple[0].strip().replace('async','')
        print(simple1)
        simple1 = simple1
        sql = "INSERT OR IGNORE INTO Corpus_4 (id,simple) VALUES (?,?)"
        conn.execute(sql,[str(index),simple1])
        index = index +1
    conn.commit()
    print ("Opened database successfully")
    conn.close()

if __name__ == '__main__':
    get()
