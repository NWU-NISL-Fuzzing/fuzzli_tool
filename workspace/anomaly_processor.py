import sqlite3
import logging
import re


logging.basicConfig(level=logging.INFO, filemode="w", filename="anomaly_processor.log")
false_positive, real_bug, unprocessed = {}, {}, []
performance_anomalies = 0


def update_dict(d, k, v):
    if k in d:
        d[k].append(v)
    else:
        d[k] = [v]


def classify(testcase, outputs, output_id, testbed_id, bug_type):
    # Check if this is a false positive triggered by ES6 features
    es6_features = ["let ", "const ", "=>", "`);", "`;", 
                    "Map", "Set", "Symbol", "Uint8Array", "Int8Array", "ArrayBuffer", 
                    "Promise", "toLocaleString", "Float32Array", "RegExp", "padStart",
                    "__defineGetter__", "decodeURIComponent", "Math.fround", "this.valueOf",
                    ".endsWith(", "Number.parseInt", "Math.sign", "Math.log2", "Object.seal", 
                    "var eval;", "console."]
    for es6_feature in es6_features:
        if es6_feature in testcase:
            # false_positive.append(output_id)
            update_dict(false_positive, "ES6", output_id)
            return True
            break
    if "Math." in testcase and testbed_id in [6, 12]:
        # false_positive.append(output_id)
        update_dict(false_positive, "ES6", output_id)
        return True
    if re.search(r"(var|const) *\{.*?\} *=", testcase) is not None:
        # false_positive.append(output_id)
        update_dict(false_positive, "ES6", output_id)
        return True
    if re.search(r",\n *\)", testcase) is not None:
        # false_positive.append(output_id)
        update_dict(false_positive, "ES6", output_id)
        return True
    if re.search(r"for.*? of ", testcase) is not None:
        # false_positive.append(output_id)
        update_dict(false_positive, "ES6", output_id)
        return True
    if re.search(r"var.*\[.*\].*\[.*\]", testcase) is not None and testbed_id in [5, 6, 11, 12]:
        # false_positive.append(output_id)
        update_dict(false_positive, "ES6", output_id)
        return True
    if len(outputs) == 6 and testbed_id in [6, 12] and "unexpected token" in outputs[5][5]:
        # false_positive.append(output_id)
        update_dict(false_positive, "ES6", output_id)
        return True
    if re.search(r"{[\s\S]+\[[\s\S]+\]:[\s\S]+}", testcase) is not None and testbed_id in [6, 12]:
        # false_positive.append(output_id)
        update_dict(false_positive, "ES6", output_id)
        return True
    if re.search(r"\[[\s\S]+\[.*?\][\s\S]+\]", testcase) is not None and testbed_id in [5, 6, 11, 12]:
        # false_positive.append(output_id)
        update_dict(false_positive, "ES6", output_id)
        return True
    # Check if this is a false positive triggered by common reasons
    false_positive_functional_features = [ "Date", "catch {", "global.", ", eval)(", "this.assert", ".name"]
    false_positive_performance_features = ["setTimeout", "clearTimeout", "setInterval"]
    for false_positive_feature in false_positive_functional_features:
        if false_positive_feature in testcase:
            # false_positive.append(output_id)
            update_dict(false_positive, "functional", output_id)
            return True
    for false_positive_feature in false_positive_performance_features:
        if false_positive_feature in testcase:
            # false_positive.append(output_id)
            update_dict(false_positive, "tmp", output_id)
            return True
    if "Error.prepareStackTrace" in testcase and testbed_id in [1, 7]:
        # false_positive.append(output_id)
        update_dict(false_positive, "functional", output_id)
        return True
    if len(outputs) == 6 and testbed_id in [6, 12] and re.search(r"[-\d\.]+", outputs[5][4]) is not None and bug_type == "Pass value *** run error":
        # false_positive.append(output_id)
        update_dict(false_positive, "functional", output_id)
        return True
    if testbed_id in [3, 9] and re.search(r"[-\d\.]+", outputs[2][4]) is not None and bug_type == "Pass value *** run error":
        # false_positive.append(output_id)
        update_dict(false_positive, "functional", output_id)
        return True
    if re.search(r"function *\(.*=.*\)", testcase) is not None:
        # false_positive.append(output_id)
        update_dict(false_positive, "functional", output_id)
        return True
    if "arguments[0]" in testcase and testbed_id in [6, 12]:
        # false_positive.append(output_id)
        update_dict(false_positive, "functional", output_id)
        return True
    if ".substr(" in testcase and testbed_id in [6, 12]:
        # false_positive.append(output_id)
        update_dict(false_positive, "functional", output_id)
        return True
    if bug_type == "Excessive time difference" and "string method mutation" in testcase:
        # false_positive.append(output_id)
        update_dict(false_positive, "performance", output_id)
        return True
    if ".values" in testcase and testbed_id in [5, 6, 11, 12] and bug_type == "Pass value *** run error":
        # false_positive.append(output_id)
        update_dict(false_positive, "functional", output_id)
        return True
    if "debugger" in testcase and testbed_id in [6, 12]:
        # false_positive.append(output_id)
        update_dict(false_positive, "functional", output_id)
        return True
    if "this.write" in testcase and testbed_id in [6, 12]:
        # false_positive.append(output_id)
        update_dict(false_positive, "functional", output_id)
        return True
    # Check if this is a real bug
    if "//regex method mutation" in testcase and testbed_id in [6, 12]:
        update_dict(real_bug, "mujs admit an invalid regular expression", output_id)
        return True
    if len(outputs) == 6 and "regexec failed" in outputs[5][5] and (testbed_id in [6, 12]):
        update_dict(real_bug, "mujs throw exception with a regular expression1", output_id)
        return True
    if len(outputs) == 6 and "regular expression" in outputs[5][5] and (testbed_id in [6, 12]):
        update_dict(real_bug, "mujs throw exception with a regular expression2", output_id)
        return True
    if testbed_id in [3, 9] and outputs[2][3] == 10:
        update_dict(real_bug, "jerryscript returncode 10", output_id)
        return True
    if "JSON.stringify" in testcase and testbed_id in [3, 9]:
        update_dict(real_bug, "jerryscript returncode 10", output_id)
        return True
    if "use strict" in testcase and testbed_id in [6, 12]:
        update_dict(real_bug, "mujs behave differently when strict mode is enabled", output_id)
        return True
    if "++ /" in testcase and testbed_id in [6, 12]:
        update_dict(real_bug, "mujs incorrectly parse '++ /'", output_id)
        return True
    if "Object.keys" in testcase and testbed_id in [6, 12]:
        update_dict(real_bug, "mujs does not box the original value", output_id)
        return True
    if "this.hasOwnProperty" in testcase and testbed_id in [6, 12]:
        update_dict(real_bug, "mujs does not support 'this.hasOwnProperty'", output_id)
        return True
    if "Object.defineProperty" in testcase and testbed_id in [6, 12]:
        update_dict(real_bug, "mujs behave differently when using Object.defineProperty", output_id)
        return True
    if "__proto__: obj.__proto__" in testcase and "Object.getOwnPropertyNames" in testcase and testbed_id in [6, 12]:
        update_dict(real_bug, "mujs throw exception", output_id)
        return True
    if "__proto__: obj.__proto__" in testcase and "Object.getOwnPropertyNames" in testcase and "[object Object]" in outputs[4][4]:
        update_dict(real_bug, "duktape output different result", output_id)
        return True
    if "Object.assign" in testcase and testbed_id in [6, 12]:
        update_dict(real_bug, "mujs does not transform true into a Boolean Object", output_id)
        return True
    if "config.anchor.x" in testcase and testbed_id in [2, 8]:
        update_dict(real_bug, "quickjs run successfully while other engines throw exception", output_id)
        return True
    if "Object.create(null)" in testcase and testbed_id in [6, 12]:
        update_dict(real_bug, "mujs does not throw exception when create a new object with null prototype", output_id)
        return True
    if outputs[3][3] == 1 and "undefined variable" in outputs[3][5] and "for (var INDEX = 0; INDEX < 1000; INDEX++)" in testcase:
        update_dict(real_bug, "xs optimize a function definition incorrectly", output_id)
        return True
    if "this.global" in testcase and testbed_id in [4, 10]:
        update_dict(real_bug, "xs defines this.global", output_id)
        return True
    if "Object.defineProperties" in testcase and testbed_id in [6, 12]:
        update_dict(real_bug, "mujs does not throw exception when transforming a wrong value to Object.defineProperties", output_id)
        return True
    if "esModule" in testcase and testbed_id in [6, 12]:
        update_dict(real_bug, "mujs throw exception when xxx", output_id)
        return True
    if "arguments[0]" in testcase and testbed_id in [1, 7]:
        update_dict(real_bug, "hermes does not support arguments", output_id)
        return True
    if ".apply(" in testcase and testbed_id in [6, 12]:
        update_dict(real_bug, "mujs does not check variable type when calling apply", output_id)
        return True
    if "Object.getOwnPropertyDescriptor" in testcase and testbed_id in [6, 12]:
        update_dict(real_bug, "mujs behave differently when calling getOwnPropertyDescriptor", output_id)
        return True
    if ".link" in testcase and testbed_id in [2, 8]:
        update_dict(real_bug, "jerryscript behave differently when calling link", output_id)
        return True
    if "JSON.stringify" in testcase and "localeCompare" in testcase and testbed_id in [4, 6, 10, 12]:
        update_dict(real_bug, "xs and mujs output incorrect results", output_id)
        return True
    if "eval" in testcase and testbed_id in [1, 7]:
        update_dict(real_bug, "hermes behave diferently when calling eval", output_id)
        return True
    if "arr.indexOf(true, Infinity)" in testcase and testbed_id in [5, 11]:
        update_dict(real_bug, "duktape incorrectly handle a extremely long array", output_id)
        return True
    if "a === ++a" in testcase and testbed_id in [5, 11]:
        update_dict(real_bug, "duktape use wrong calculation order", output_id)
        return True
    if " = Object.create(" in testcase and testbed_id in [6, 12]:
        update_dict(real_bug, "mujs outputs different results when calling Object.create", output_id)
        return True
    # If not satisfied above conditions
    return False


def main():
    global false_positive, real_bug, unprocessed, performance_anomalies

    db_file = 'fuzzli-ablation.db'
    # db_file = 'fuzzlil.db'
    db = sqlite3.connect(db_file)
    cursor = db.cursor()
    sql1 = "SELECT bug_type, output_id FROM DifferentialTestResults;"
    cursor.execute(sql1)
    output_ids = cursor.fetchall()
    for bug_type, output_id in output_ids:
        sql2 = f"SELECT testcase_id, testbed_id FROM Outputs where id = {output_id};"
        cursor.execute(sql2)
        # print(cursor.fetchone())
        testcase_id, testbed_id = cursor.fetchone()
        sql3 = f"SELECT * FROM Outputs where testcase_id = {testcase_id};"
        cursor.execute(sql3)
        outputs = cursor.fetchall()
        sql4 = f"SELECT testcase FROM Testcases where id = {testcase_id};"
        cursor.execute(sql4)
        testcase = cursor.fetchone()[0]
        if bug_type in ["Timeout", "Excessive time difference"]:
            performance_anomalies += 1
        processed = classify(testcase, outputs, output_id, testbed_id, bug_type)
        if not processed:
            unprocessed.append(output_id)
    unprocessed = list(set(unprocessed) - set(false_positive))
    with open("processed.txt", "r") as f:
        processed = eval(f.read())
    todo = [15538, 15544, 15550, 15556, 15562, 15568, 15580, 15586, 15592, 15598, 70708, 70720, 77581, 77605,
            127436, 127437, 127439, 127442, 127443, 127445, 127448, 127449, 127451, 127454, 127455, 127457, 
            127460, 127461, 127463, 127466, 127467, 127469, 127472, 127473, 127475, 127490, 127491, 127493]
    # processed = []
    # todo = []
    unprocessed = list(set(unprocessed) - set(processed) - set(todo))
    print("false_positive_functional:", len(false_positive["functional"]))
    print("false_positive_performance:", len(false_positive["performance"]))
    print("false_positive_es6:", len(false_positive["ES6"]))
    false_positive_performance_rate = len(false_positive["performance"]) / len(output_ids)
    print("false_positive_performance_rate:", false_positive_performance_rate)
    print("real_bug:", len(real_bug))
    print("unprocessed:", len(unprocessed))
    # 按升序排序
    unprocessed = sorted(unprocessed)
    logging.info("unprocessed:"+str(unprocessed))
    logging.info("real_bug:"+str(real_bug))
    print("performance_anomalies:", performance_anomalies)

if __name__ == "__main__":
    main()
