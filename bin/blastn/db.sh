#!/bin/bash
set -ue

fasta=${1}
db=${2}

echo "START: create blastn database from ${fasta}"
makeblastdb -dbtype nucl \
            -in ${fasta} -out ${db} \
#            -logfile /dev/null
echo "DONE: ${db}"
