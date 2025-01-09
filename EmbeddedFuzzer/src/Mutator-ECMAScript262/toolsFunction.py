class Point:
    def __init__(self, line, column):
        self.line = line
        self.column = column


class Location:
    def __init__(self, start: Point, end: Point):
        self.start = start
        self.end = end


def find_all(substr: str, original_string: str):
    sub_length = len(substr)
    index_list = []
    index = original_string.find(substr)
    while index != -1:
        if index + sub_length < len(original_string) - 1:
            if original_string[index + sub_length + 1] == "(":
                index_list.append([index, index + sub_length])
            elif original_string[index: index + sub_length + 1].strip() == original_string[index: index + sub_length]:
                raise Exception("Match error")
        index = original_string.find(substr, index + 1)
    return index_list

