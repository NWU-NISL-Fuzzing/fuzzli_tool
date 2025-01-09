
import json
import pathlib

from db import db_operation







def get_tested_count() -> int:
    config_path = "../resources/config.json"
    with open(config_path, "r") as f:
        config = json.load(f)

    db_path = pathlib.Path(config["db_path"])
    
    return db_operation.DBOperation(str(db_path)).query_tested_count()
    


print(get_tested_count())
