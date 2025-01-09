import pathlib


def init_data(simples_dir: str, suffix: str = "*.js") -> list:
    """

    :param simples_dir:
    :param suffix:
    :return:
    """
    path = pathlib.Path(simples_dir)
    content_list = []
    for file in path.rglob(suffix):
        content_list.append(file.read_text())
    return content_list
