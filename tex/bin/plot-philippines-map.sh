#!/bin/bash

current_dir="$(pwd)"

image_dir="$(dirname $current_dir)/images"

./plot-philippines-map.R

cd "$image_dir"

for p in map-*.pdf
do
    pdfcrop "$p" "$p"
done

for p in grid-*.tex
do
    latexmk -pdf "$p"
done

for p in grid-*.pdf
do
    pdfcrop "$p" "$p"
done

cd "$current_dir"
