from typing import List


class TestbedParser:
    def __init__(self, testbeds: List[str]):
        self.common_dir_depth = self.get_common_dir_depth(testbeds)
    
    
    def get_common_dir_depth(self, testbeds) -> int:
        if len(testbeds) < 2:
            raise LookupError(f"The number of engines is less than 2 and cannot be tested")
        path_a = testbeds[0].split("/")
        path_b = testbeds[-1].split("/")
        for index in range(min(len(path_a), len(path_b))):
            if path_a[index] != path_b[index]:
                return index
        raise Exception("Unable to extract the public path of testbeds")

    def get_engine_name(self, testbed: str):
        return testbed.split("/")[self.common_dir_depth]

    def get_engine_version(self, testbed: str):
        return testbed.split("/")[self.common_dir_depth + 1]
