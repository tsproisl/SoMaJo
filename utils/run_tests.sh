#!/bin/bash

SCRIPTDIR=$(dirname $BASH_SOURCE)
cd $SCRIPTDIR/..

# Test Discovery
python3 -m unittest discover
