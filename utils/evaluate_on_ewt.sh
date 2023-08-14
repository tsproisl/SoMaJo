#!/bin/bash

SCRIPTDIR=$(dirname $BASH_SOURCE)
cd $SCRIPTDIR

mkdir tmp
for f in ../data/English_Web_Treebank/en-ud-*.txt
do
    filename=$(basename $f)
    somajo-tokenizer -l en_PTB $f > tmp/$filename
done
echo "GOLD"
# perl ../data/empirist_gold_standard/tools/compare_tokenization.perl -e errors_ewt.txt tmp ../data/English_Web_Treebank/gold
./evaluate.py -d -e errors.txt tmp/ ../data/English_Web_Treebank/gold/
# echo ""
# echo "SEMIGOLD"
# perl ../data/empirist_gold_standard/tools/compare_tokenization.perl -e errors_ewt_semi.txt tmp ../data/English_Web_Treebank/semigold
rm -r tmp/
