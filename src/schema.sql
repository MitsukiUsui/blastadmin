CREATE TABLE fasta
(
    fasta_id TEXT PRIMARY KEY,
    origin TEXT,
    timestamp TEXT
);
CREATE TABLE db
(
    fasta_id TEXT,
    software TEXT,
    timestamp TEXT,
    PRIMARY KEY (fasta_id, software)
);
