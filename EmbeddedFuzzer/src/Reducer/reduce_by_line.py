import Result
from Reducer import simplifyTestcaseCore


def sample_by_statement(init_result: Result.HarnessResult):

    new_bug_harness_result_list = []
    original_test_case = init_result.testcase.strip()
    
    test_case_last_list = original_test_case.split("\n")  
    tmp_test_case_list = test_case_last_list[:]  
    loop_counter = 0
    
    for index in range(2):
        loop_counter += 1
        
        for row in range(len(tmp_test_case_list) - 1, -1, -1):  
            tmp = tmp_test_case_list[:]
            
            tmp.pop(row)
            [removable, new_bug] = simplifyTestcaseCore.is_removable(init_result, "\n".join(tmp))
            if new_bug is not None:
                new_bug_harness_result_list.append(new_bug)
            if removable:
                
                tmp_test_case_list = tmp[:]  
        if len(test_case_last_list) == len(tmp_test_case_list):  
            
            break
        test_case_last_list = tmp_test_case_list[:]
        
    reduced_test_case = "\n".join(test_case_last_list)
    return [reduced_test_case, new_bug_harness_result_list]
