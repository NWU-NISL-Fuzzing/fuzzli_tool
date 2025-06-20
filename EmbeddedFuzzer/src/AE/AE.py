import pathlib


def init_data(samples_dir: str, suffix: str = "*.js") -> list:
    """

    :param samples_dir:
    :param suffix:
    :return:
    """
    path = pathlib.Path(samples_dir)
    content_list = []
    for file in path.rglob(suffix):
        content_list.append(file.read_text())
    return content_list
