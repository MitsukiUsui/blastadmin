#!/bin/bash
set -ue

fasta=${1}
db=${2}

makeblastdb -dbtype nucl \
            -in ${fasta} -out ${db} \
#            -logfile /dev/null
