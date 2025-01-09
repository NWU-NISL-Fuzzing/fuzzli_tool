











from ResultFilter.errorinfo_classifier.errorinfo_classifier import errorinfo_classify
from ResultFilter.errorinfo_classifier.errorinfo_db_operation import DataBase




if __name__ == '__main__':
    from tqdm import tqdm
    import json

    test_data_file = 'ty_test_data.json'
    db_path = 'mysql://debian-sys-maint:stkbZxAzV9X3D72q@10.15.0.26:3306/classify?charset=utf8'

    with open(test_data_file, encoding='utf-8') as f:
        content = json.loads(f.read())
    db_connection = DataBase(db_path)
    for i in tqdm(content):
        
        i.append('NoApi')
        i.append(1)
        
        i[2] = {i[1]:i[2]}
        result, type_id = errorinfo_classify(i, db_connection)
        if result:
            print(f"{i[1]}{i[2]} new {type_id}")
        else:
            print(f"{i[1]}{i[2]} old {type_id}")
        

    print(f"Finish, stored in {db_path}.")
