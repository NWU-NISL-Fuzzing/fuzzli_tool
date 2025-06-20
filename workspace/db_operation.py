#coding=utf-8
import sqlite3

def get():
    conn = sqlite3.connect('top2000corpus-20200410-FX-SF.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS Corpus_4(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sample BLOB NOT NULL,
    used INTEGER default 0,

    UNIQUE(sample)
    );
''')
    print ("Table created successfully")
    samples = conn.execute("select sample from Corpus limit 15000,5000")
    list1 = list(list(items) for items in list(samples))  
    # print(list1)
    print ("Records created successfully")
    index = 1
    for sample in list1 :
        sample1 = sample[0].strip().replace('async','')
        print(sample1)
        sample1 = sample1
        sql = "INSERT OR IGNORE INTO Corpus_4 (id,sample) VALUES (?,?)"
        conn.execute(sql,[str(index),sample1])
        index = index +1
    conn.commit()
    print ("Opened database successfully")
    conn.close()

if __name__ == '__main__':
    get()
