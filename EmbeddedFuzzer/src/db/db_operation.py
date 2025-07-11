
import pathlib
import sqlite3

from Result import *


class DBOperation:
    def __init__(self, db_path: str):  
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def close(self):
        self.conn.close()

    def create_tables(self):
        cursor = self.conn.cursor()
        sql_file_path = pathlib.Path("../EmbeddedFuzzer/src/db/tables.sql").absolute().resolve()
        sql_list = [e for e in sql_file_path.read_text().replace("\n", "").split(";") if e != '']
        try:
            for sql in sql_list:
                cursor.execute(sql)
            self.conn.commit()
        except BaseException as e:
            self.conn.rollback()
            raise e

    def query_corpus(self, unused_only=True) -> List[str]:
        sql = "select sample from Corpus"
        if unused_only:
            sql = "select sample from Corpus WHERE used=0"
        testcases = [e[0] for e in self.query_template(sql)]
        return testcases

    def query_template(self, sql: str, values: list = None) -> list:
        cursor = self.conn.cursor()
        try:
            if values is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, values)
            
            result = cursor.fetchall()
        except BaseException as e:
            raise e
        finally:
            cursor.close()
        return result

    def insert_original_testcase(self, testcase: str, sample: str) -> int:
        sql = "select id from Corpus where sample=?"
        sample_id = self.query_template(sql, [sample])[0][0]
        sql_insert = "insert or ignore into OriginalTestcases(testcase, sample_id) values(?,?)"
        original_testcase_id = self.insert_template(sql_insert, [testcase, sample_id])
        if original_testcase_id is None:  
            query_id_sql = "select id from OriginalTestcases where testcase=?"
            original_testcase_id = self.query_template(query_id_sql, [testcase])[0][0]
        return original_testcase_id

    def insert_harness_result(self, harness_result: HarnessResult, original_testcase_id: int) -> list:
        cursor = self.conn.cursor()
        insert_testcase_sql = f"INSERT OR IGNORE INTO Testcases (original_testcase_id,testcase) VALUES(?,?)"
        insert_engines_sql = f"INSERT OR IGNORE INTO Engines (testbed) VALUES(?)"
        insert_harness_result_sql = f"INSERT OR ignore INTO Outputs(" \
                                    f"testcase_id,testbed_id,returncode,stdout,stderr," \
                                    f"duration_ms,event_start_epoch_ms) " \
                                    f"VALUES(?,?,?,?,?,?,?)"
        max_str_len = int((2 ** 15-1) / 2)  
        try:
            cursor.execute(insert_testcase_sql, [original_testcase_id, harness_result.testcase])            
            if cursor.rowcount == 0:
                return [None, None]
            testcase_id = cursor.lastrowid
            for output in harness_result.outputs:
                read_result = self.query_template("SELECT id FROM Engines WHERE testbed=?", [output.testbed])
                # print("size of read_result:", len(read_result))
                if len(read_result) == 0:  
                    cursor.execute(insert_engines_sql, [output.testbed])
                    testbed_id = cursor.lastrowid
                else:
                    testbed_id = read_result[0][0]
                cursor.execute(insert_harness_result_sql, [
                    testcase_id, testbed_id, output.returncode, str(output.stdout)[:max_str_len],
                    str(output.stderr)[:max_str_len], output.duration_ms, output.event_start_epoch_ms])
                output.id = cursor.lastrowid
            self.conn.commit()
        except BaseException as e:
            file=open("../results/result.txt","w")
            file.write(str(testcase_id))
            file.write("-")
            file.write(str(testbed_id))
            file.write("--")
            file.write(str(output.returncode))
            file.write("---")
            file.write(str(output.stdout)[:max_str_len])
            file.write("----")
            file.write(str(output.stderr)[:max_str_len])
            file.write("-----")
            file.write(str(output.duration_ms))
            file.write(str(output.event_start_epoch_ms))
            file.close()
            self.conn.rollback()
            raise e
        finally:
            cursor.close()
        return [harness_result, testcase_id]
    
    def insert_differential_test_results(self, bugs_info_list: List[DifferentialTestResult],testcase:str):
        cursor = self.conn.cursor()
        insert_diff_test_result_sql = f"INSERT OR IGNORE INTO DifferentialTestResults (" \
                                      f"bug_type,output_id,classify_result,classify_id) " \
                                      f"VALUES(?,?,?,?)"
        try:
            for bug_info in bugs_info_list:
                # bug_info.output_id=self.query_outputs_id(testcase, bug_info.output_id)
                # print("bug_info.output_id:", bug_info.output_id)
                cursor.execute(insert_diff_test_result_sql, [bug_info.bug_type, bug_info.output_id,
                                                             bug_info.classify_result, bug_info.classify_id])
            self.conn.commit()
        except BaseException as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()

    def insert_corpus(self, sample: str) -> int:
        sql = f"INSERT OR IGNORE INTO Corpus (sample) VALUES(?)"
        return self.insert_template(sql, [sample])

    def insert_template(self, sql: str, values: list) -> int:
        cursor = self.conn.cursor()
        identify = None
        try:
            cursor.execute(sql, values)
            if cursor.rowcount != 0:
                identify = cursor.lastrowid
            self.conn.commit()
        except BaseException as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()
        return identify

    def insert_auto_simplified_testcase(self, testcase_id: int, auto_simplified_testcase: str, simplified_duration_ms):
        cursor = self.conn.cursor()
        sql = f"UPDATE Testcases set auto_simplified_testcase=?, auto_simplified_duration_ms=? where id=?;"
        try:
            cursor.execute(sql, [auto_simplified_testcase, simplified_duration_ms, testcase_id])
            self.conn.commit()
        except BaseException as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()

    def update_sample_status(self, sample: str):
        cursor = self.conn.cursor()
        sql = "update Corpus set used=1 WHERE sample=?"
        try:
            cursor.execute(sql, [sample])
            self.conn.commit()
        except BaseException as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()

    def query_mutated_test_case(self, test_case_id: int = -1, limit: int = -1):
        if test_case_id != -1:
            sql = "SELECT id, testcase FROM Testcases WHERE id=?;"
            return self.query_template(sql, [test_case_id])
        else:
            if limit > 0:
                # sql = "SELECT id, testcase FROM Testcases WHERE auto_simplified_testcase NOT NULL AND is_manual_check = 0 LIMIT ?;"
                sql = "SELECT id, testcase FROM Testcases WHERE is_manual_check = 0 LIMIT ?;"
                return self.query_template(sql, [limit])
            else:
                # sql = "SELECT id, testcase FROM Testcases WHERE auto_simplified_testcase NOT NULL AND is_manual_check = 0;"
                sql = "SELECT id, testcase FROM Testcases WHERE is_manual_check = 0;"
                return self.query_template(sql)

    def query_mutated_test_case_randomly(self):
        
        # TODO. 三个sql的定义，用哪个？
        sql = "SELECT id, testcase FROM Testcases WHERE auto_simplified_testcase NOT NULL AND is_manual_check = 0 " \
              "order by RANDOM() limit 1;"
        
        sql = """SELECT id, testcase FROM Testcases WHERE auto_simplified_testcase NOT NULL AND is_manual_check = 0 AND Testcases.id in (select distinct(O.testcase_id) from Outputs O INNER JOIN DifferentialTestResults D WHERE O.id=D.output_id AND D.bug_type="Performance issue") order by RANDOM() limit 1;"""
       
        sql = """SELECT id, testcase FROM Testcases WHERE is_manual_check = 0 AND Testcases.id in (select distinct(O.testcase_id) from Outputs O INNER JOIN DifferentialTestResults D WHERE O.id=D.output_id AND D.bug_type="Performance issue") limit 1;"""
        return self.query_template(sql)
    
    def query_anomalies(self):
        sql = "SELECT * FROM DifferentialTestResults"
        return self.query_template(sql)
    
    def query_results_by_output_id(self, output_id: int):
        sql1 = "SELECT testcase_id FROM Outputs WHERE id=?"
        res1 = self.query_template(sql1, [output_id])
        sql2 = "SELECT * FROM Outputs WHERE testcase_id=?"
        res2 = self.query_template(sql2, [res1[0][0]])
        return res2

    def update_test_case_manual_checked_state(self, test_case_id: int):
        cursor = self.conn.cursor()
        sql = "update Testcases set is_manual_check=1 WHERE id=?"
        try:
            cursor.execute(sql, [test_case_id])
            self.conn.commit()
        except BaseException as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()

    def query_tested_count(self) -> int:
        sql = "select count(*) from Corpus where used = 1;"
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql)
            result = cursor.fetchall()[0][0]
        except BaseException as e:
            raise e
        finally:
            cursor.close()
        return result
   
    def query_testcases(self) -> List[str]:
        sql = "select testcase from OriginalTestcases limit 10"
        testcases = [e[0] for e in self.query_template(sql)]
        return testcases

    def insert_testcase(self, testcase: str) -> int:
        sql_insert = "insert or ignore into OriginalTestcases(testcase) values(?)"
        original_testcase_id = self.insert_template(sql_insert, [testcase])
        if original_testcase_id is None: 
            query_id_sql = "select id from OriginalTestcases where testcase=?"
            original_testcase_id = self.query_template(query_id_sql, [testcase])[0][0]
        return original_testcase_id

    def insert_corpus1(self, sample: str) -> int:
        sql = "INSERT OR IGNORE INTO Corpus(sample) VALUES(?)"
        return self.insert_template(sql, [sample])

    def query_testcases_id(self, testcase: str) -> int:
        sql = "select id from OriginalTestcases where testcase=?"
        original_testcase_id = self.query_template(sql, [testcase])[0][0]
        return original_testcase_id    
   
    def query_flag(self, id: int) -> int:
        sql="SELECT corpus.flag FROM corpus JOIN OriginalTestcases ON corpus.id = OriginalTestcases.sample_id WHERE OriginalTestcases.id = ?"
        flag = self.query_template(sql, [id])[0][0]
        return flag
  
    def query_outputs_id(self, testcase: str, testbed_id: int) -> int:
        sql = "SELECT Outputs.id FROM Outputs JOIN Testcases ON Outputs.testcase_id = Testcases.id WHERE Testcases.testcase = ? and testbed_id=?"
        values = (testcase, testbed_id)
        result = self.query_template(sql, values)
        if result:
            return result[0][0]
        else:
            return -1 
    
    def commit(self):
        self.conn.commit()
