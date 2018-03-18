#!/bin/bash

set -ue

query=${1}
database=${2}
result=${3}

blastn -db ${database}\
       -query ${query}\
       -out ${result}\
       -word_size 4\
       -evalue 1e-3\
       -outfmt 6
