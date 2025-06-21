import json
import typing

from ResultFilter.errorinfo_classifier.errorinfo_db_operation import ErrorType


def errorinfo_classify(info_list: typing.List, db_connection) -> [bool, int]:
    engine_name = info_list[1]
    error_info = json.dumps(info_list[2])  
    error_api = info_list[3]
    error_type = info_list[4]  
    Error = ErrorType(engine=engine_name, error_info=error_info, error_api=error_api, error_type=error_type)
    result, type_id = db_connection.query_and_compare(Error)
    if result:
        type_id = db_connection.add(Error)
    return [result, type_id]
