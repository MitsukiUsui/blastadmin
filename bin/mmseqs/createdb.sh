#!/bin/bash
set -ue

fastaFilepath=${1}
dbFilepath=${2}

mmseqs createdb ${fastaFilepath} ${dbFilepath}
mmseqs createindex ${dbFilepath}
