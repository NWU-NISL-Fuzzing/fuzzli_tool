from utils.JSASTOpt import *


class Uniform:
    def __init__(self, prefix: str = "NISL"):
        self.prefix = prefix
        self.variable_name = []
        self.old_2_new_dict = {}

    def uniform_variable_name(self, js_code: str):

        self.variable_name = []
        self.old_2_new_dict = {}
        js_ast = build_ast(js_code)
        self.get_ast_variable_name(js_ast)
        self.create_old_2_new_name_dict()
        self.replace_js_variable_name(js_ast)
        return generate_es_code(js_ast)

    def get_ast_variable_name(self, node: dict):

        for key, values in node.items():
            
            if key == "loc":
                continue
            if key == "id" and type(values) == dict and values["type"] == "Identifier":
                self.variable_name.append(values["name"])
            elif key == "params" and type(values) == list:
                for child_node in values:
                    if type(child_node) == dict and child_node["type"] == "Identifier":
                        self.variable_name.append(child_node["name"])
            if type(values) == list:
                for child_node in values:
                    self.get_ast_variable_name(child_node)
            elif type(values) == dict:
                self.get_ast_variable_name(values)  

    def replace_js_variable_name(self, node: dict):

        for key, values in node.items():
            if key == "loc":
                continue
            self.replace(values)
            if type(values) == list:
                for child_node in values:
                    self.replace(child_node)
                    self.replace_js_variable_name(child_node)
            elif type(values) == dict and key != "loc":
                self.replace_js_variable_name(values)  

    def replace(self, node: dict):

        if type(node) == dict and node.__contains__("type") and node["type"] == "Identifier" \
                and self.old_2_new_dict.__contains__(node["name"]):
            node["name"] = self.old_2_new_dict[node["name"]]

    @staticmethod
    def generate_variable_name(num: int, prefix: str = ""):

        name_list = []
        
        for index in range(num):
            
            name = prefix + chr(122) * (int(index / 26)) + chr(97 + index % 26)
            name_list.append(name)
        return name_list

    def create_old_2_new_name_dict(self):
        """

        :return:
        """
        new_name_list = self.generate_variable_name(len(self.variable_name), self.prefix)
        index = 0
        for old_name in self.variable_name:
            
            if not self.old_2_new_dict.__contains__(old_name):
                
                self.old_2_new_dict[old_name] = new_name_list[index]
                index += 1


if __name__ == '__main__':
    import pathlib
    testcase = pathlib.Path("./test/testcase.js").read_text()
    uniform = Uniform("nisl")
    uniformed_test_case = uniform.uniform_variable_name(testcase)
    print(uniformed_test_case)

