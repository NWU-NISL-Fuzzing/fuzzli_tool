import collections
import json
import math

from typing import List


class Output:
    def __init__(self,
                 id_db: int,
                 testbed: str,
                 returncode: int,
                 stdout: str,
                 stderr: str,
                 duration_ms: int,
                 event_start_epoch_ms: int):
        self.id = id_db
        self.testbed = testbed
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.duration_ms = duration_ms
        self.event_start_epoch_ms = event_start_epoch_ms
        self.output_class = self.get_output_class()

    def get_output_class(self) -> str:

        if self.returncode == -9 and self.duration_ms > 30 * 1000:
            return "timeout"
        elif self.returncode < 0:
            return "crash"
        elif self.returncode > 0 or not self.stderr == "":
            return "script_error"        
        else:
            return "pass"

    def serialize(self):
        return {"id": self.id,
                "testbed": self.testbed,
                "returncode": self.returncode,
                "stdout": self.stdout,
                "stderr": self.stderr,
                "duration_ms": self.duration_ms,
                "event_start_epoch_ms": self.event_start_epoch_ms}

    def __str__(self):
        return json.dumps({"id": self.id,
                           "testbed": self.testbed,
                           "returncode": self.returncode,
                           "stdout": self.stdout,
                           "stderr": self.stderr,
                           "duration_ms": self.duration_ms,
                           "event_start_epoch_ms": self.event_start_epoch_ms},
                          indent=4)


class HarnessResult:
    def __init__(self, testcase: str):
        self.testcase = testcase
        self.outputs = []

    def add_output(self, output: Output):
        self.outputs.append(output)

    def __str__(self):
        return json.dumps({"Harness Result": {"testcase": self.testcase,
                                              "outputs": [e.serialize() for e in self.outputs]
                                              }
                           }, indent=4)


class DifferentialTestResult:
    def __init__(self, bug_type: str, output_id: int, testbed: str):
        self.bug_type = bug_type
        self.output_id = output_id
        self.testbed = testbed
        self.classify_result = None
        self.classify_id = None

    def serialize(self):
        return {"Differential Test Result": {"bug_type": self.bug_type,
                                             "output_id": self.output_id,
                                             "testbed": self.testbed,
                                             "classify_result": self.classify_result,
                                             "classify_id": self.classify_id
                                             }}

    def __str__(self):
        return json.dumps(self.serialize(), indent=4)


Majority = collections.namedtuple('Majority', [  
    'majority_outcome', 'outcome_majority_size',
    'majority_stdout', 'stdout_majority_size'
])


def get_majority_output(result: HarnessResult) -> Majority:
    """Majority vote on testcase outcomes and outputs."""
    
    majority_outcome, outcome_majority_size = collections.Counter([
        output.output_class for output in result.outputs
    ]).most_common(1)[0]
    
    majority_stdout, stdout_majority_size = collections.Counter([
        output.stdout for output in result.outputs
    ]).most_common(1)[0]
    return Majority(majority_outcome, outcome_majority_size,
                    majority_stdout, stdout_majority_size)


def get_min_duration(result: HarnessResult) -> int:
    min_duration = int(1e10)
    for output in result.outputs:
        if output.output_class == "pass":
            min_duration = min(min_duration, output.duration_ms)
    return min_duration


def differential_test(result: HarnessResult) -> List[DifferentialTestResult]:
    if result is None:  
        return []
    performance_factor = 10  
    ratio = 2 / 3
    majority = get_majority_output(result)
    testbed_num = len(result.outputs)
    bugs_info = []
    for output in result.outputs:
        if output.output_class == "crash":
            bugs_info.append(DifferentialTestResult("Crash", output.id, output.testbed))
        elif majority.majority_outcome != output.output_class and majority.outcome_majority_size >= math.ceil(
                ratio * testbed_num):
            if majority.majority_outcome == "pass":
                bugs_info.append(DifferentialTestResult("Most pass *** run error", output.id, output.testbed))
            elif majority.majority_outcome == "timeout" and majority.outcome_majority_size != testbed_num:
                bugs_info.append(DifferentialTestResult("Timeout", output.id, output.testbed))
                # pass
            elif majority.majority_outcome == "Crash":
                bugs_info.append(DifferentialTestResult("Most crash *** run error", output.id, output.testbed))
            elif majority.majority_outcome == "script_error":
                bugs_info.append(DifferentialTestResult("Most script error *** run error", output.id, output.testbed))
        elif output.output_class == "pass" and majority.majority_outcome == output.output_class and \
                output.stdout != majority.majority_stdout and \
                majority.stdout_majority_size >= math.ceil(ratio * majority.outcome_majority_size):
            if majority.outcome_majority_size >= math.ceil(ratio * testbed_num):
                bugs_info.append(DifferentialTestResult("Pass value *** run error", output.id, output.testbed))
    bugs_info = performance_test(result, bugs_info, performance_factor)
    return bugs_info


def performance_test(result: HarnessResult, bugs_info: List[DifferentialTestResult], performance_factor) \
        -> List[DifferentialTestResult]:
    abnormal_output_id_set = {info.output_id for info in bugs_info}
    non_abnormal_outputs = [output for output in result.outputs if not abnormal_output_id_set.__contains__(output.id)]
    if len(non_abnormal_outputs) < 1:
        return bugs_info
    min_duration = min([output.duration_ms for output in non_abnormal_outputs])
    for output in non_abnormal_outputs:
        # if output.output_class == "pass" and output.duration_ms > min_duration * performance_factor:
        if output.duration_ms > min_duration * performance_factor:
            bugs_info.append(DifferentialTestResult("Excessive time difference", output.id, output.testbed))
    return bugs_info
