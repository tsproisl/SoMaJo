#!/bin/bash

SCRIPTDIR=$(dirname $BASH_SOURCE)
cd $SCRIPTDIR

mkdir tmp
for f in ../data/Ortmann_et_al/txt/*.txt
do
    filename=$(basename $f)
    ../bin/somajo-tokenizer --split-sentences $f > tmp/$filename
done
perl ../data/empirist_gold_standard/tools/compare_tokenization.perl -e errors_test.txt tmp ../data/Ortmann_et_al/tokens
./evaluate.py -d --sentences -e errors.txt tmp/ ../data/Ortmann_et_al/tokens/
rm -r tmp/
