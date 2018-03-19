#!/bin/bash
set -ue

fasta=${1}
db=${2}

mmseqs createdb ${fasta} ${db}
