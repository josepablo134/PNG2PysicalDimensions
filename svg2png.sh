#! /bin/bash

input_folder=$1
output_folder=$2

if [[ -z "$input_folder" ]]; then
    echo "$0 [input_folder] [output_folder]"
    exit -1
fi
if [[ -z "$output_folder" ]]; then
    echo "$0 [input_folder] [output_folder]"
    exit -1
fi
if [[ ! -d $input_folder ]]; then
    echo "directory $input_folder doesn't exists"
    exit -1
fi

if [[ ! -d $output_folder ]]; then
     mkdir -p $output_folder
fi

convert_image(){
    input_file=$1
    output_file=$2
    echo convert -density 600 $input_file $output_file
    convert -density 600 $input_file $output_file
}

for input_file in "$input_folder"/*.svg; do
    output_file=$output_folder/"${input_file##*/}"
    output_file="${output_file%.svg}".png
    convert_image $input_file $output_file
done

