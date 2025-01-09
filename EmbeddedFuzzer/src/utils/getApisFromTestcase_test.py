import json
import pathlib

from utils import getApisFromTestcase

if __name__ == '__main__':
    testcase = pathlib.Path("./data/tmp/testcase.js").read_text()
    node_info_path = "./data/tmp/testcase-node-info.json"
    config_path = "./data/config.json"
    
    with open(config_path, "r") as f:
        config = json.load(f)
    class_method_path = config["ESApis"]["classMethod"]
    prototype_method_path = config["ESApis"]["prototypeMethod"]
    constructor_path = config["ESApis"]["constructor"]
    function_path = config["ESApis"]["function"]
    instance = getApisFromTestcase.ESAPI(config["ESApis"])
    nodes = instance.parse_function_nodes(testcase)
    counter = instance.count_es_apis_in_testcase(nodes)
    fre = instance.statistical_apis_frequency()
    tmp = {"testcase": testcase, "nodes": nodes, "counter": counter}
    with open(node_info_path, "w+") as f:
        json.dump(tmp, f)
    breakpoint()
