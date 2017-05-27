#!/bin/bash

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

rm -rf "$SCRIPTDIR"/networks/* 
rm "$SCRIPTDIR"/trainsets/*
rm "$SCRIPTDIR"/densities/*.raw
find "$SCRIPTDIR" -name "*.pyc" -exec rm '{}' +
find "$SCRIPTDIR" -name "*.pyo" -exec rm '{}' +
