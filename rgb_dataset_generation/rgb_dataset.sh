#!/bin/bash
# generate rgb dataset
dir=/mnt/scratch
rm -r $dir/NYU-EventVPR-RGB/
echo "Purged previous dataset directory"
python $dir/rgb_dataset_generation/generate_dataset.py \
       --dir $dir/NYU-EventVPR-RGB \
       --tolerance 25 \
       --factor 0.01
       
