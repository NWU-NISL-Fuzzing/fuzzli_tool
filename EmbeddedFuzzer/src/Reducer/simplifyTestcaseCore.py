import math

import Result
from Harness import Harness
from ResultFilter import classify


def check_effective(testcase: str, before_harness_result: Result.HarnessResult):

    before_bug_info = Result.differential_test(before_harness_result)

    testbeds = [output.testbed for output in before_harness_result.outputs]
    harness = Harness(engines=testbeds)
    after_harness_result = harness.run_testcase(testcase)

    
    after_harness_result = rectify_output_id(before_harness_result, after_harness_result)
    after_bug_info = Result.differential_test(after_harness_result)
    
    
    
    
    
    
    if len(after_bug_info) != len(before_bug_info):
        return [False, after_harness_result if len(after_bug_info) > 0 else None]

    
    before_suspicious_id_set = set([e.output_id for e in before_bug_info])
    after_suspicious_id_set = set([e.output_id for e in after_bug_info])
    
    if len(before_suspicious_id_set.union(after_suspicious_id_set)) > len(before_suspicious_id_set):
        return [False, after_harness_result]

    
    testbed_output_class_dict = {output.testbed: output.output_class for output in before_harness_result.outputs}
    for output in after_harness_result.outputs:
        if not testbed_output_class_dict[output.testbed] == output.output_class:
            return [False, after_harness_result]

    
    before_output_id_bug_ype_dict = {e.output_id: e.bug_type for e in before_bug_info}
    for info in after_bug_info:
        if not before_output_id_bug_ype_dict[info.output_id] == info.bug_type:
            return [False, after_harness_result]

    

    
    performance_output_id = set([e.output_id for e in after_bug_info if e.bug_type == "Performance issue"])
    if len(performance_output_id) > 0:


        
        
        
        [before_suspicious_outputs, before_normal_outputs] = split_output(before_harness_result)
        
        before_shortest_time = min([output.duration_ms for output in before_normal_outputs])
        
        before_id_duration_dict = {output.id: output.duration_ms
                                   for output in before_harness_result.outputs if
                                   performance_output_id.__contains__(output.id)}
        
        
        before_testbeds_gap_dict = {bed: math.floor(duration / before_shortest_time) for bed, duration in
                                    before_id_duration_dict.items()}

        [after_suspicious_outputs, after_normal_outputs] = split_output(after_harness_result)
        
        after_shortest_time = min([output.duration_ms for output in after_normal_outputs])
        after_id_duration_dict = {output.id: output.duration_ms
                                  for output in after_harness_result.outputs if
                                  performance_output_id.__contains__(output.id)}
        after_testbeds_gap_dict = {bed: (duration / after_shortest_time) for bed, duration in
                                   after_id_duration_dict.items()}
        for bed, gap in before_testbeds_gap_dict.items():
            if after_testbeds_gap_dict[bed] < gap:  
                return [False, None]

    return [True, None]


def rectify_output_id(before_harness_result: Result.HarnessResult,
                      after_harness_result: Result.HarnessResult) -> Result.HarnessResult:

    engine_id_dict = {output.testbed: output.id for output in before_harness_result.outputs}
    for output in after_harness_result.outputs:
        output.id = engine_id_dict[output.testbed]
    return after_harness_result

'''

def split_output(result: Result.HarnessResult, bug_info: Result.DifferentialTestResult):

    
    
    print("this code need")
    differential_result_output_ids = [info.output_id for info in bug_info]
    suspicious_output_ids_set = set(differential_result_output_ids)
    suspicious_output = []
    normal_output = []
    for output in result.outputs:
        if suspicious_output_ids_set.__contains__(output.id):
            suspicious_output.append(output)
        else:
            normal_output.append(output)

    return [suspicious_output, normal_output]
'''

def split_output(result: Result.HarnessResult):

    
    
    differential_result_output_ids = [info.output_id for info in Result.differential_test(result)]
    suspicious_output_ids_set = set(differential_result_output_ids)
    suspicious_output = []
    normal_output = []
    for output in result.outputs:
        if suspicious_output_ids_set.__contains__(output.id):
            suspicious_output.append(output)
        else:
            normal_output.append(output)
    return [suspicious_output, normal_output]



def is_removable(harness_result: Result.HarnessResult, code: str):
    return check_effective(code, harness_result)


def get_key_outputs(output: Result.Output):

    key_outputs = classify.list_essential_exception_message(output.stderr + output.stdout)
    if key_outputs == "":
        key_outputs = output.stdout
    return key_outputs
