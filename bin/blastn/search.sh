#!/bin/bash

set -ue

queryFilepath=${1}
dbFilepath=${2}
resultFilepath=${3}

blastn -db ${dbFilepath}\
       -query ${queryFilepath}\
       -out ${resultFilepath}\
       -word_size 8\
       -evalue 1e-3\
       -outfmt 6
