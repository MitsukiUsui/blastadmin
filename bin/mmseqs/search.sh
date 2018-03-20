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
mmseqs search ${queryDB} ${targetDB} ${resultDB} ${tmpDirec} --threads 20
mmseqs convertalis ${queryDB} ${targetDB} ${resultDB} ${resultFilepath} --threads 20
