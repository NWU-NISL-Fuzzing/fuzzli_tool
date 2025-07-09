import sqlite3
import random

# 连接到源数据库 a.db
conn_a = sqlite3.connect('top2000corpus-20230106-FX-SF.db')
cursor_a = conn_a.cursor()

# 获取 Corpus 表的所有列名
cursor_a.execute("PRAGMA table_info(Corpus)")
columns_info = cursor_a.fetchall()
columns = [col[1] for col in columns_info]
columns_str = ', '.join(columns)
placeholders = ', '.join(['?'] * len(columns))

# 从 Corpus 中随机选取 60000 条记录
cursor_a.execute(f"SELECT COUNT(*) FROM Corpus")
total_count = cursor_a.fetchone()[0]

if total_count < 60000:
    raise ValueError("Corpus 表中数据不足 60000 条")

cursor_a.execute(f"SELECT rowid FROM Corpus")
all_rowids = [row[0] for row in cursor_a.fetchall()]
sample_rowids = random.sample(all_rowids, 60000)

# 使用 rowid 抽取对应记录
placeholders_rowid = ','.join(['?'] * len(sample_rowids))
cursor_a.execute(f"SELECT {columns_str} FROM Corpus WHERE rowid IN ({placeholders_rowid})", sample_rowids)
sampled_data = cursor_a.fetchall()

# 连接到目标数据库 b.db
conn_b = sqlite3.connect('fuzzlil-60000.db')
cursor_b = conn_b.cursor()

# 创建 Corpus 表（如果还不存在，结构与 a.db 相同）
columns_schema = ', '.join([f"{col[1]} {col[2]}" for col in columns_info])
cursor_b.execute(f"CREATE TABLE IF NOT EXISTS Corpus ({columns_schema})")

# 插入抽样数据到 b.db 的 Corpus 表
cursor_b.executemany(f"INSERT INTO Corpus ({columns_str}) VALUES ({placeholders})", sampled_data)

# 提交并关闭连接
conn_b.commit()
conn_a.close()
conn_b.close()

print("已成功将60000条随机记录从a.db迁移至b.db")
