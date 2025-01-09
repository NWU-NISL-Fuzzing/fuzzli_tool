CREATE TABLE IF NOT EXISTS Corpus(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    simple BLOB NOT NULL,
    used INTEGER default 0,

    UNIQUE(simple)
    );

CREATE UNIQUE INDEX IF NOT EXISTS Corpus_simple_index on Corpus(simple);

CREATE TABLE IF NOT  EXISTS OriginalTestcases(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    testcase BLOB NOT NULL,
    simple_id INTEGER,

    FOREIGN KEY (simple_id) REFERENCES Corpus(id),
    UNIQUE(testcase)
    );

CREATE UNIQUE INDEX  IF NOT EXISTS orginal_testcase_index on OriginalTestcases(testcase);

CREATE TABLE IF NOT  EXISTS Testcases(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_testcase_id INTEGER NOT NULL DEFAULT 0,
    testcase BLOB NOT NULL,
    auto_simplified_testcase BLOB DEFAULT NULL,
    auto_simplified_duration_ms INTEGER DEFAULT 0,
    manual_simplified_testcase BLOB DEFAULT NULL,
    is_manual_check INTEGER DEFAULT 0,

    FOREIGN KEY (original_testcase_id) REFERENCES OriginalTestcases(id),
    UNIQUE(testcase)
    );

CREATE UNIQUE INDEX  IF NOT EXISTS testcase_testcase_index on Testcases(testcase);

CREATE TABLE IF NOT EXISTS Engines(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    testbed BLOB NOT NULL,
    engine_name BLOB DEFAULT NULL,
    version BLOB DEFAULT NULL,
    mode BLOB DEFAULT NULL,

    UNIQUE(testbed)
    );

CREATE UNIQUE INDEX  IF NOT EXISTS engine_testbed_index on Engines(testbed);

CREATE TABLE IF NOT EXISTS Outputs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    testcase_id INTEGER NOT NULL,
    testbed_id INTEGER NOT NULL,
    returncode INTEGER DEFAULT NULL,
    stdout BLOB DEFAULT NULL,
    stderr BLOB DEFAULT NULL,
    duration_ms INTEGER DEFAULT NULL,
    event_start_epoch_ms INTEGER DEFAULT NULL,

    FOREIGN KEY (testcase_id) REFERENCES Testcases(id),
    FOREIGN KEY (testbed_id) REFERENCES Engines(id),
	UNIQUE(testcase_id, testbed_id)
    );

CREATE TABLE IF NOT EXISTS DifferentialTestResults(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bug_type BLOB NOT NULL ,
    output_id INTEGER NOT NULL UNIQUE,

    classify_result INTEGER DEFAULT null,
    classify_id INTEGER DEFAULT null,

    bug_lable INTEGER DEFAULT NULL,
    reason BLOB DEFAULT NULL,
    assignee BLOB DEFAULT NULL,
    submit_date INTEGER DEFAULT NULL,
    remarks BLOB DEFAULT NULL,

    FOREIGN KEY (output_id) REFERENCES Outputs(id)
    );