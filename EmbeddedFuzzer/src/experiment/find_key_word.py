import pathlib
import re

key_regex = "sdafdfa"
key_patter = re.compile(key_regex)
work_dirs = [e for e in pathlib.Path("../workspace/experiment/fuzzilli").iterdir()]
index = 0
for work_dir in work_dirs[:]:
    index += 1
    
    

    if len(str(work_dir).split("-")) != 3:
        continue
    js_files = [e for e in work_dir.rglob("*.js")]
    if len(js_files) == 1:
        continue
    print(index)
    print("=========" * 30)
    print(f"index: {index}")
    print(work_dir)
    print(len(js_files))
    print("=========" * 30)
    for e in js_files:
        txt = e.read_text()
        result = key_patter.search(txt)
        if result is None:
            print("==" * 50)
            print(txt)
            breakpoint()
