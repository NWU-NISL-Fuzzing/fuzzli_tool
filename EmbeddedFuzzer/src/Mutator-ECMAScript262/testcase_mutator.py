import json

from Configer import Config
from Mutator import getMutatedTestcase
from utils import crypto


def mutate(testcase, config: Config) -> set:

    index = crypto.md5_str(str(testcase))
    mutated_testcase_set = set()
    if testcase.__contains__("NISLFuzzingFunc"):
        nodes = config.api_instance.parse_function_nodes(testcase)
        if len(nodes) > 0:
            counter = config.api_instance.count_es_apis_in_testcase(nodes)
            api_node_info = {"testcase": testcase, "nodes": nodes, "counter": counter}
            
            api_node_info_path = (config.workspace / f"api-node-information/{index}.json")
            api_node_info_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(api_node_info_path, "w+") as f:
                json.dump(api_node_info, f)
            mutated_testcase_set = set(getMutatedTestcase.mutate_testcase(api_node_info_path))
    mutated_testcase_set.add(testcase)
    return mutated_testcase_set
