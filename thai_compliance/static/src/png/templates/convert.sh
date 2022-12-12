#!/usr/bin/env bash

for i in ../../pdf/templates/*.pdf;
do
    convert -density 300 -depth 8 -background white -alpha remove -alpha off -strip $i "PNG32:`basename ${i%.pdf}.png`";
done