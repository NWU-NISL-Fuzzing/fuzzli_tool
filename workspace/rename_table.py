import sqlite3

# 连接到数据库
conn = sqlite3.connect('top2000corpus-20230106-FX-SF.db')
cursor = conn.cursor()

# 获取表结构，获取除了simple之外的所有列名
cursor.execute("PRAGMA table_info(Corpus)")
columns_info = cursor.fetchall()
columns = [col[1] for col in columns_info]

# 替换列名 simple -> sample
new_columns = ['sample' if col == 'simple' else col for col in columns]

# 构建新表字段定义（保持数据类型一致）
new_column_defs = []
for col in columns_info:
    col_name = 'sample' if col[1] == 'simple' else col[1]
    new_column_defs.append(f"{col_name} {col[2]}")
new_column_defs_str = ", ".join(new_column_defs)

# 创建新表
cursor.execute(f"CREATE TABLE Corpus_new ({new_column_defs_str})")

# 拷贝数据
old_columns_str = ", ".join(columns)
new_columns_str = ", ".join(new_columns)
cursor.execute(f"INSERT INTO Corpus_new ({new_columns_str}) SELECT {old_columns_str} FROM Corpus")

# 删除原表并重命名新表
cursor.execute("DROP TABLE Corpus")
cursor.execute("ALTER TABLE Corpus_new RENAME TO Corpus")

# 提交并关闭连接
conn.commit()
conn.close()
