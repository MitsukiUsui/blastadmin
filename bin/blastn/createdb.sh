#!/bin/bash
set -ue

fastaFilepath=${1}
dbFilepath=${2}

makeblastdb -dbtype nucl \
            -in ${fastaFilepath} -out ${dbFilepath} \
