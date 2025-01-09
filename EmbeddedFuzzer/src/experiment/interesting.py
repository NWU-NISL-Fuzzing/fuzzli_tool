import pathlib
import pickle

from Harness import Harness
from Reducer.simplifyTestcaseCore import check_effective


def interesting(argv, prefix):
    harness_path = pathlib.Path(prefix).absolute().resolve().parent / "harness_result.txt"
    testcase_path = pathlib.Path(argv[0]).absolute().resolve()
    if not harness_path.exists():
        
        testbeds = [
            "../engines/hermes/hermes-0.12.0/build_release/bin/hermes -w",
            "../engines/quickjs/quickjs-2021-03-27/qjs",
            "../engines/jerryscript/jerryscript-bd1c4df/release/jerryscript/build/bin/jerry",
            "../engines/XS/moddable-3.7.6/build/bin/lin/release/xst",
            "../engines/duktape/duktape-2.7.0/duk",
            "../engines/mujs/mujs-1.3.2/build/release/mujs"
        ]
        harness = Harness(testbeds)
        harness_path.write_bytes(pickle.dumps(harness.run_testcase(testcase_path.read_text())))
        return True
    if not testcase_path.exists():
        raise FileNotFoundError(f"Not exist: {testcase_path}")
    harness_result = pickle.loads(harness_path.read_bytes())
    testcase = testcase_path.read_text()
    return check_effective(testcase, harness_result)[0]
