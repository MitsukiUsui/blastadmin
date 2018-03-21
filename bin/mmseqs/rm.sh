#!/bin/bash

dbFilepath=${1}

rm -f ${dbFilepath}
rm -f ${dbFilepath}_h
rm -f ${dbFilepath}_h.index
rm -f ${dbFilepath}.*

