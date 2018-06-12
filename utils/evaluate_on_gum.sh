#!/bin/bash

SCRIPTDIR=$(dirname $BASH_SOURCE)
cd $SCRIPTDIR

mkdir tmp
for f in ../data/GUM/text/*
do
    filename=$(basename $f)
    ../bin/somajo-tokenizer -l en $f > tmp/$filename
done
perl ../data/empirist_gold_standard/tools/compare_tokenization.perl -e errors_ewt.txt tmp ../data/GUM/tokenized
rm -r tmp/
