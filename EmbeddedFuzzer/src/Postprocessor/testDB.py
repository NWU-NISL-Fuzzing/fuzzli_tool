from db_operation import DBOperation

if __name__ == '__main__':
    db_op = DBOperation(r"C:\Users\Implementist\Desktop\test.db", "corpus")
    column_names = ["Content", "Number"]
    values = [["hahaha", 3875678],["xixixi", 47865],["heiheihei", 6345]]
    db_op.init_db()
    db_op.insert(column_names, values)
    db_op.finalize()