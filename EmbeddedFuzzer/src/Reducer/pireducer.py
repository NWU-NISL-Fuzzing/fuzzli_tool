from sklearn.cluster import KMeans
import numpy as np
import subprocess
import json
import time
import math
import os
import re

""" Gloabl Variable Definitions """

# bug_type = "timeout"
# bug_type = "etd"
bug_type = "performance"
NODE_PATH = "/home/fuzzli_tool/EmbeddedFuzzer/node_modules"
INSTRUMENT_JS_PATH = "/home/fuzzli_tool/EmbeddedFuzzer/src/Reducer/instrument.js"
# TESTCASE_PATH = f"/home/fuzzli_tool/workspace/reduction-{bug_type}-20250717"
TESTCASE_PATH = f"/home/fuzzli_tool/workspace/fuzzlia-random-100"
if not os.path.exists(TESTCASE_PATH):
    os.makedirs(TESTCASE_PATH)
    print("Create TESTCASE_PATH.")
else:
    print("TESTCASE_PATH already exist.")

""" Small Tools """

def write_down(filename: str, code: str):
    with open(filename, "w") as f:
        f.write(code)

def int_list_to_str(l: list):
    """ [1, 2, 3] => 1,2,3 """
    new_l = []
    for i in l:
        new_l.append(str(i))
    return ",".join(new_l)

""" Parse and Modify JS Code """

def transform_js_code(original: str) -> str:
    """ Split complex statements into simple statements. """

    result = subprocess.run([
        "npx", "babel", original,
        "--plugins", "/home/fuzzli_tool/EmbeddedFuzzer/src/Reducer/decompose_complex_stmt.js"
    ], capture_output=True, text=True)
    if result.returncode != 0:
        print("Babel transform failed:")
        print(result.stderr)
        return None
    return result.stdout

def instrument_code(js_code):
    """
    Instrument the code to get the execution time of each line.
    Only the leaf nodes in main function are instrumented.
    """

    main_func = js_code[:js_code.index("\n};\n")+3]
    print("main_func:\n"+main_func)
    process = subprocess.Popen(
        ['node', INSTRUMENT_JS_PATH],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, "NODE_PATH": NODE_PATH}
    )
    stdout, stderr = process.communicate(input=main_func)

    if process.returncode != 0:
        raise RuntimeError(f"Babel instrumentation failed:\n{stderr}")

    return stdout+js_code[js_code.index("\n};\n")+3:]

def get_variables_on_line(filename: str, target_line: list):
    """ Get the variable names on the target line. """

    print("target_line:", target_line)
    try:
        result = subprocess.run(
            ['node', 'analyze_vars.js', filename, int_list_to_str(target_line)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        return eval(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error running Node script:", e.stderr)
        return []

def run_js(filename, testbed_id):
    """ Run the instrumented JS file using specific JS engine and return the execution time of each line. """

    testbed = {
        1: "/home/fuzzli_tool/engines/hermes/hermes-0.12.0/build_release/bin/hermes",
        2: "/home/fuzzli_tool/engines/quickjs/quickjs-2021-03-27/qjs",
        3: "/home/fuzzli_tool/engines/jerryscript/jerryscript-2.4.0/jerryscript-2.4.0/build/bin/jerry",
        4: "/home/fuzzli_tool/engines/XS/moddable-3.7.0/build/bin/lin/release/xst",
        5: "/home/fuzzli_tool/engines/duktape/duktape-2.7.0/duk",
        6: "/home/fuzzli_tool/engines/mujs/mujs-1.3.2/build/release/mujs",
        7: "/home/fuzzli_tool/engines/hermes/hermes-0.12.0/build_release/bin/hermes",
        8: "/home/fuzzli_tool/engines/quickjs/quickjs-2021-03-27/qjs",
        9: "/home/fuzzli_tool/engines/jerryscript/jerryscript-2.4.0/jerryscript-2.4.0/build/bin/jerry",
        10: "/home/fuzzli_tool/engines/XS/moddable-3.7.0/build/bin/lin/release/xst",
        11: "/home/fuzzli_tool/engines/duktape/duktape-2.7.0/duk",
        12: "/home/fuzzli_tool/engines/mujs/mujs-1.3.2/build/release/mujs"
    }
    # result = subprocess.run(["timeout", "-s", "TERM", "30", testbed[testbed_id], filename], capture_output=True, text=True)
    cmd = ['stdbuf', '-oL', testbed[testbed_id], filename]
    print("cmd:", cmd)
    # start = time.time()
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = proc.communicate(timeout=30)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
    # end = time.time()
    # print("time:", end-start)
    # print("stdout:", stdout)
    # print("sterr:", stderr)
    d0_time_dict, d1_time_dict = {}, {}
    inst_num_match = re.search(r"Total Instrumented: ([0-9]+)", stdout)
    inst_num = int(inst_num_match.group(1))
    for line in re.finditer(r"leaf_stmt\_([0-9]+) (.*)", stdout):
        stmt_num = int(line.group(1))
        try:
            duration = float(line.group(2))
        except:
            print("match:", line.group())
        if stmt_num in d1_time_dict:
            d1_time_dict[stmt_num] += duration
        else:
            d1_time_dict[stmt_num] = duration
    print("d1_time_dict:", d1_time_dict)
    sorted_d1_time_dict = dict(sorted(d1_time_dict.items(), key=lambda item: item[1], reverse=True))
    return sorted_d1_time_dict, inst_num

def classify_exec_time(exec_times):
    """ Classify the execution time of each statement into two groups (delete or not). """

    if len(exec_times) == 1:
        return [], exec_times
    to_be_deleted, to_be_kept = [], []
    # K-means algorithm.
    times = np.array([[v] for v in exec_times.values()])
    kmeans = KMeans(n_clusters=2, n_init='auto', random_state=0).fit(times)
    initial_labels = kmeans.labels_
    cluster_means = [np.mean(times[initial_labels == i]) for i in range(2)]
    smaller_cluster_label = np.argmin(cluster_means)
    # Classify statements into two groups.
    for i, stmt_idx in enumerate(exec_times.keys()):
        if initial_labels[i] == smaller_cluster_label:
            to_be_deleted.append(stmt_idx)
        else:
            to_be_kept.append(stmt_idx)
    print("to_be_kept:", to_be_kept)
    return to_be_deleted, to_be_kept

def delete_node(filename, to_be_deleted):
    """ Delete the statements in the to_be_deleted list. """

    try:
        result = subprocess.run(
            ['node', 'delete_node.js', filename, to_be_deleted],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("Error running Node script:", e.stderr)
        return None

def delete_node_without_vars(filename: str, to_be_deleted: str, var_list: str):
    """ Delete the statements in the to_be_deleted list without the protected variables. """

    if type(to_be_deleted) != str:
        raise TypeError("to_be_deleted should be a string")
    try:
        cmd = ['node', 'delete_node_without_vars.js', filename, to_be_deleted, var_list]
        print("cmd:"+" ".join(cmd))
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("Error running Node script:", e.stderr)
        return None

def delete_useless_stmt(filename, sorted_d1_time_dict, inst_num):
    # Situation 1. Test case is interrupted in the first statement.
    if len(sorted_d1_time_dict) == 0:
        to_be_deleted = set(range(inst_num)) - set([0])
        to_be_deleted = list(to_be_deleted)
        deleted = delete_node(filename, int_list_to_str(to_be_deleted))
    else:
        # Situation 2. Statements that successfully execute all spend 0s.
        if list(sorted_d1_time_dict.values()).count(0.0) == len(sorted_d1_time_dict):
            to_be_deleted = sorted_d1_time_dict.keys()
            to_be_deleted = list(to_be_deleted)
            to_be_kept = set(range(inst_num)) - set(to_be_deleted)
        # Situation 3. Statements that successfully execute spend more than 0s.
        elif list(sorted_d1_time_dict.values()).count(0.0) != len(sorted_d1_time_dict):
            # 如果有语句的运行时间未统计上，补全再进行分类
            if len(sorted_d1_time_dict) != inst_num:
                for i in range(inst_num):
                    if i not in sorted_d1_time_dict:
                        sorted_d1_time_dict[i] = 30.0
                for k, v in sorted_d1_time_dict.items():
                    if math.isnan(v):
                        sorted_d1_time_dict[k] = 30.0
            to_be_deleted, to_be_kept = classify_exec_time(sorted_d1_time_dict)
        else:
            raise Exception("unexpected situations!")
        print("to_be_kept:", to_be_kept)
        # The statements after longest lines can be deleted directly
        if len(to_be_kept) == 0 and len(to_be_deleted) == inst_num:
            to_be_kept = to_be_deleted
            to_be_deleted = []
        max_longest_line = max(to_be_kept)
        to_be_deleted_before, to_be_deleted_after = [], []
        for i in to_be_deleted:
            if i > max_longest_line:
                to_be_deleted_after.append(i)
            else:
                to_be_deleted_before.append(i)
        if len(to_be_deleted_after) > 0:
            print("存在可以直接删除的行：", to_be_deleted_after)
            deleted = delete_node(filename, int_list_to_str(to_be_deleted_after))
            print("deleted:\n"+deleted)
            write_down(filename, deleted)
        # Obtain variables used in to_be_kept
        var_list = get_variables_on_line(filename, to_be_kept)
        print("var_list:", var_list)
        deleted = delete_node_without_vars(filename, int_list_to_str(to_be_deleted_before), ",".join(var_list))
    print("to_be_deleted:", to_be_deleted)
    return deleted

def remove_dead_code(reduced_path, postprocessed_path):
    """ Use terser remove dead code. """

    # 替换_tmp1等变量名
    with open(reduced_path, "r") as f:
        postprocessed = f.read()
    for var_name in re.finditer(r"var (tmp[0-9]+)=(.*?);", postprocessed):
        postprocessed = postprocessed.replace(var_name.group(0), "")
        postprocessed = postprocessed.replace(var_name.group(1), var_name.group(2))
    # 删除变量赋值语句外循环
    # print("im here")
    # print(postprocessed)
    var_dec_in_loop = re.search(r"for \(var INDEX = 0; INDEX < 1000; INDEX\+\+\) \{[\s]+(var NISLParameter[0-9]+ = [\s\S]+?)\n\}", postprocessed)
    if var_dec_in_loop:
        # print("存在循环多次定义变量")
        postprocessed = postprocessed.replace(var_dec_in_loop.group(0), var_dec_in_loop.group(1))
        # print(postprocessed)
    write_down(postprocessed_path, postprocessed)
    # 删除调用主函数时无用的参数
    try:
        result = subprocess.run(
            ['node', 'remove_unused_args.js', postprocessed_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        write_down(postprocessed_path, result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error running Node script:", e.stderr)
    # 用terser进行压缩
    try:
        subprocess.run([
            "terser", postprocessed_path,
            "--compress",
            "dead_code=true,unused=true,conditionals=true,toplevel=true",
            "--beautify",
            "-o", postprocessed_path
        ], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print("Terser Error:", e.stderr)

def main():
    # with open(f"/home/fuzzli_tool/workspace/{bug_type}.json", "r") as f:
    with open("/home/reduce/fuzzlia_random_100/performance_bugs_fuzzlia.json", "r" ) as f:
        data = json.load(f)
    result = ""
    print("total:", len(data))
    for i, d in enumerate(data):
        print("processing:", i)
        # if i != 12:
        #     continue
        testcase_id = d["testcase_id"]
        original_path = TESTCASE_PATH+f"/{i}.js"
        print("original_path:", original_path)
        testcase = d["testcase"]
        write_down(original_path, testcase)
        # 0. split complex statements into simple statements
        splited = transform_js_code(original_path)
        splited_path = TESTCASE_PATH+f"/{i}_splited.js"
        write_down(splited_path, splited)
        # 1. instrument testcase
        instrumented = instrument_code(splited)
        # print(instrumented)
        instrumented_path = TESTCASE_PATH+f"/{i}_instrumented.js"
        write_down(instrumented_path, instrumented)
        # 2. run instrumented testcase
        sorted_d1_time_dict, inst_num = run_js(instrumented_path, d["testbed_id"])
        # 3. delete useless codes
        reduced = delete_useless_stmt(splited_path, sorted_d1_time_dict, inst_num)
        reduced_path = TESTCASE_PATH+f"/{i}_reduced.js"
        write_down(reduced_path, reduced)
        # 4. remove dead code
        postprocessed_path = TESTCASE_PATH+f"/{i}_postprocessed.js"
        postprocessed = remove_dead_code(reduced_path, postprocessed_path)
        # Store time dictionary.
        result += f"{sorted_d1_time_dict}\n"
        # break
    result_path = f"{bug_type}_result.txt"
    write_down(result_path, result)

def run_one():
    # with open("test.js", "r") as f:
    #     testcase = f.read()

    # bug_type = "timeout"
    # with open(f"/home/fuzzli_tool/workspace/{bug_type}.json", "r") as f:
    #     data = json.load(f)
    # d = data[-2]
    # testcase = d["testcase"]

    # print(">>> Original JavaScript:\n")
    # print(testcase)

    # with open("/home/fuzzli_tool/workspace/reduction-etd-20250701/tmp.js", "r") as f:
    #     content = f.read()
    # instrumented = instrument_code(content)
    # print("\n>>> Instrumented JavaScript:\n")
    # print(instrumented)

    # print("\n>>> Execution Output:\n")
    # sorted_d1_time_dict, inst_num = run_js(instrumented, d["testbed_id"])
    # print(sorted_d1_time_dict)
    # print(inst_num)

    # print(delete_useless_stmt("test.js", {}, 9))
    
    # print(get_variables_on_line("test.js", [4,5]))

    # print(delete_node_without_vars("test.js", "4, 5", "NISLe,NISLb,NISLc"))

    # classify_exec_time({1: 2760.0, 2: 8074.0})

    # sorted_d1_time_dict, inst_num = run_js('/home/fuzzli_tool/workspace/reduction-20250628/1362_instrumented.js', 4)

    # print(transform_js_code("test.js"))

    with open("/home/fuzzli_tool/workspace/reduction-performance-20250717-44/0_reduced.js", "r") as f:
        content = f.read()
    var_dec_in_loop = re.search(r"for \(var INDEX = 0; INDEX < 1000; INDEX\+\+\) \{[\s]+(var NISLParameter[0-9]+ = [\s\S]+?)\n\}", content)
    if var_dec_in_loop:
        content = content.replace(var_dec_in_loop.group(0), var_dec_in_loop.group(1))
    print(content)

if __name__ == "__main__":
    main()
    # run_one()
