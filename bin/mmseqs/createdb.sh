#!/bin/bash
set -ue

fastaFilepath=${1}
dbFilepath=${2}

tmpDirec=/var/tmp/${USER}/mmseqs/`date +%s`
mkdir -p ${tmpDirec}

mmseqs createdb ${fastaFilepath} ${dbFilepath}
mmseqs createindex ${dbFilepath} ${tmpDirec} --threads 30
