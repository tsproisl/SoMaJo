#!/bin/bash

SCRIPTDIR=$(dirname $BASH_SOURCE)
cd $SCRIPTDIR

mkdir tmp
for f in ../../data/empirist_test_pos_web/raw/*
do
    filename=$(basename $f)
    ../bin/tokenizer --split_camel_case $f > tmp/$filename
done
perl ../../data/empirist_test_pos_web/tools/compare_tokenization.perl -e errors_test.txt tmp ../../data/empirist_test_pos_web/tokenized
rm -r tmp/
