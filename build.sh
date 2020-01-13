#!/bin/bash

rm -r package function.zip 2> /dev/null

docker run -v $(pwd):/result/ lambci/lambda:build-python3.8 \
    /bin/bash -c "cd /result/ && pip3.8 install --target ./package lxml"

pushd ./package 
zip -r9 ../function.zip .
popd
zip -j function.zip scraper.py
