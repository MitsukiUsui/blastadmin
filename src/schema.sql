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
CREATE TABLE history
(
    software TEXT,
    query TEXT,
    database TEXT,
    result TEXT,
    hash_param TEXT,
    hash_query TEXT,
    hash_database TEXT,
    hash_result TEXT
);
