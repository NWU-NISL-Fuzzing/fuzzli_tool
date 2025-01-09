from Result import HarnessResult


def remove_from(provider: list, recipient: list) -> list:
    for e in provider:
        recipient.remove(e)
    return recipient


def list_intersection(list1: list, list2: list) -> list:
    
    return sorted(list(set(list1).intersection(set(list2))))


def get_identifiers(result: HarnessResult) -> list:
    identifiers = []
    for engine in result.outputs:
        identifiers.append(engine.id)
    return identifiers
