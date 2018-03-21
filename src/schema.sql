CREATE TABLE fasta
(
    id TEXT PRIMARY KEY,
    filepath TEXT,
    origin TEXT,
    timestamp TEXT
);
CREATE TABLE db
(
    id TEXT,
    software TEXT,
    filepath TEXT,
    timestamp TEXT,
    PRIMARY KEY (id, software)
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
