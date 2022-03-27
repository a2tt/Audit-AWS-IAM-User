#! /bin/bash

if [ ! -d package ]; then
  mkdir package
fi
cd package

pip install -r ../requirements.txt --target .
zip -r9 ../function.zip *

cd ..
zip -g function.zip *.py