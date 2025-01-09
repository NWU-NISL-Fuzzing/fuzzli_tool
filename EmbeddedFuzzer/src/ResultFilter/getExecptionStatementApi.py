import logging
import re

from utils.getApisFromTestcase import ESAPI


def locate_exception_statement_line_number(exception_message):

    if exception_message.__contains__("warning: ") or exception_message.__contains__("note: "):  
        pattern = "(Error:)(.|\n)+?(javascriptTestcase_[^:]*:)([0-9]+)"
    else:
        pattern = "(javascriptTestcase_[^:]*:)([0-9]+)"
    try:
        result = re.search(pattern, exception_message)
        
        row = result.groups()[-1]
        return int(row)
    except Exception as e:
        pass
    pattern2 = "(Error:(.|\n)+?)(\\[)(line: )([0-9]+)+(, column: )([0-9]+)(])"  
    try:
        result = re.search(pattern2, exception_message)
        row = result.groups()[-4]
        return int(row)
    except Exception as e:
        return None


def get_specified_line_api(api_nodes, line):

    try:
        for node in api_nodes:
            
            if int(node["callee"]["loc"]["start"]["line"]) <= line <= int(node["callee"]["loc"]["end"]["line"]):
                return node["ESAPI"]["name"]
    except Exception as e:
        logging.debug("Failed to get API on specified line!")
    return None


def get_exception_statement_api(esapi_instance: ESAPI, testcase: str, exception_message: str, api_nodes=None):

    line_number_in_exception = locate_exception_statement_line_number(exception_message)
    
    if line_number_in_exception is None:
        return [None, None]
    if api_nodes is None:
        
        api_nodes = esapi_instance.parse_function_nodes(testcase)
    return [get_specified_line_api(api_nodes, line_number_in_exception), api_nodes]
