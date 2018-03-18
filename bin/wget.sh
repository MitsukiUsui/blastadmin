#!/bin/bash

set -eu

ftp=${1}
out=${2}

if echo ${ftp} | grep -q .gz; then
    wget --timeout 120 --quiet -O - ${ftp} | gunzip -c > ${out}
else
    wget --timeout 120 --quiet -O ${out} ${ftp}
fi
