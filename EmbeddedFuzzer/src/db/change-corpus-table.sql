
ALTER TABLE corpus RENAME TO tableOld;
CREATE TABLE IF NOT EXISTS Corpus(id INTEGER PRIMARY KEY AUTOINCREMENT,sample BLOB NOT NULL,used INTEGER default 0,UNIQUE(sample));
CREATE UNIQUE INDEX IF NOT EXISTS Corpus_sample_index on Corpus(sample);
INSERT Or IGNORE INTO Corpus(sample) SELECT Content as sample FROM tableOld;
SELECT COUNT(*) FROM Corpus;
SELECT COUNT(*) FROM  tableOld;
drop table tableOld;



UPDATE Corpus SET used=0 WHERE used=1;
DROP TABLE OriginalTestcases;
DROP TABLE Testcases;
DROP TABLE Engines;
DROP TABLE Outputs;
DROP TABLE DifferentialTestResults;