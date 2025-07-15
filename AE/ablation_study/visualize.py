import os

# folders = ["fuzzli", "fuzzlil", "fuzzlia", "fuzzlir", "fuzzlis", "fuzzlio"]
folders = ["fuzzli"]
for folder in folders:
    bug_count = {}
    for f in os.listdir(folder):
        if f.startswith("duktape"):
            bug_count["duktape"] = bug_count.get("duktape", 0) + 1
        elif f.startswith("hermes"):
            bug_count["hermes"] = bug_count.get("hermes", 0) + 1
        elif f.startswith("jerryjs"):
            bug_count["jerryjs"] = bug_count.get("jerryjs", 0) + 1
        elif f.startswith("mujs"):
            bug_count["mujs"] = bug_count.get("mujs", 0) + 1
        elif f.startswith("quickjs"):
            bug_count["quickjs"] = bug_count.get("quickjs", 0) + 1
        elif f.startswith("xs"):
            bug_count["xs"] = bug_count.get("xs", 0) + 1
# 用表格展示
print("Engine\tCount")
for engine, count in bug_count.items():
    print(f"{engine}\t{count}")
print("Total\t"+str(sum(bug_count.values())))    