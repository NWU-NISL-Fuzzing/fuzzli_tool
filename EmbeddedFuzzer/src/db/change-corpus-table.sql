
ALTER TABLE corpus RENAME TO tableOld;
CREATE TABLE IF NOT EXISTS Corpus(id INTEGER PRIMARY KEY AUTOINCREMENT,simple BLOB NOT NULL,used INTEGER default 0,UNIQUE(simple));
CREATE UNIQUE INDEX IF NOT EXISTS Corpus_simple_index on Corpus(simple);
INSERT Or IGNORE INTO Corpus(simple) SELECT Content as simple FROM tableOld;
SELECT COUNT(*) FROM Corpus;
SELECT COUNT(*) FROM  tableOld;
drop table tableOld;



UPDATE Corpus SET used=0 WHERE used=1;
DROP TABLE OriginalTestcases;
DROP TABLE Testcases;
DROP TABLE Engines;
DROP TABLE Outputs;
DROP TABLE DifferentialTestResults;