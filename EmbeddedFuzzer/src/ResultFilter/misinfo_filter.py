












def filtering_rules(engine_name: str, key_exception: str) -> bool:
    flag = True
    
    if engine_name.strip().lower() == 'hermes' and key_exception.strip().startswith('note:'):
        flag = False

    

    return flag


