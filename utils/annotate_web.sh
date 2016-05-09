#!/bin/bash

SCRIPTDIR=$(dirname $BASH_SOURCE)
cd $SCRIPTDIR

for f in ../../data/empirist_test_tok_web/raw/*
do
    filename=$(basename $f)
    ../bin/tokenizer --split_camel_case $f > ../../data/web_tok_SoMaJo/$filename
    # ../bin/tokenizer $f > ../../data/web_tok_SoMaJo/$filename
done
perl ../../data/empirist_test_tok_web/tools/validate_tokenization.perl -x ../../data/web_tok_SoMaJo/ ../../data/empirist_test_tok_web/raw/
