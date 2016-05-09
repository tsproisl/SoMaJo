#!/bin/bash

SCRIPTDIR=$(dirname $BASH_SOURCE)
cd $SCRIPTDIR

mkdir tmp
for f in ../../data/all_test/raw/*
# for f in ../../data/empirist_test_pos_cmc/raw/*
# for f in ../../data/empirist_test_pos_web/raw/*
do
    filename=$(basename $f)
    sed -re "/^<[^>]+>$/! { s/([.!?,;:+*()\"'–])/ \1 /g; s/\s+/\n/g }" $f > tmp/$filename
done
perl ../../data/empirist_test_pos_web/tools/compare_tokenization.perl -x -e errors_baseline_test.txt tmp ../../data/all_test/tokenized
# perl ../../data/empirist_test_pos_web/tools/compare_tokenization.perl -e errors_test.txt tmp ../../data/empirist_test_pos_cmc/tokenized
# perl ../../data/empirist_test_pos_web/tools/compare_tokenization.perl -e errors_test.txt tmp ../../data/empirist_test_pos_web/tokenized
rm -r tmp/
