#!/bin/bash

SCRIPTDIR=$(dirname $BASH_SOURCE)
cd $SCRIPTDIR

mkdir tmp
for f in ../data/empirist_gold_standard/test_cmc/raw/*
do
    filename=$(basename $f)
    ../bin/somajo-tokenizer --split_camel_case $f > tmp/$filename
done
# perl ../data/empirist_gold_standard/tools/compare_tokenization.perl -e errors_test.txt tmp ../data/empirist_gold_standard/test_cmc/tokenized
./evaluate.py -d -e errors.txt --ignore-xml tmp/ ../data/empirist_gold_standard/test_cmc/tokenized/
rm -r tmp/
