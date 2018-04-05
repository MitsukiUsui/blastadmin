#!/bin/bash

set -ue

queryFilepath=${1}
dbFilepath=${2}
resultFilepath=${3}

mmseqsDirec=/var/tmp/${USER}/mmseqs/`date +%s`
queryDB=${mmseqsDirec}/queryDB
targetDB=${dbFilepath}
resultDB=${mmseqsDirec}/resultDB
tmpDirec=${mmseqsDirec}/tmp

mkdir -p ${mmseqsDirec}
mkdir -p ${tmpDirec}

mmseqs createdb ${queryFilepath} ${queryDB}
mmseqs search ${queryDB} ${targetDB} ${resultDB} ${tmpDirec} --threads 30 --start-sens 1 --sens-steps 3 -s 7
mmseqs convertalis ${queryDB} ${targetDB} ${resultDB} ${resultFilepath} --threads 30
