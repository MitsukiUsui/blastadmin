#!/bin/bash

set -ue

query=${1}
targetDB=${2}
result=${3}

mmseqsDirec=/var/tmp/mitsuki/mmseqs/`date +%s`
queryDB=${mmseqsDirec}/queryDB
resultDB=${mmseqsDirec}/resultDB
tmpDirec=${mmseqsDirec}/tmp

mkdir -p ${mmseqsDirec}
mkdir -p ${tmpDirec}

mmseqs createdb ${query} ${queryDB}
mmseqs search ${queryDB} ${targetDB} ${resultDB} ${tmpDirec} --threads 20
mmseqs convertalis ${queryDB} ${targetDB} ${resultDB} ${result} --threads 20
