#!/bin/bash

# define hyperparams
type="event" # choices: event, reconstructed, rgb

#############################################################################################################################################
# define paths 
raw=/home/taiyi/scratch2/NYU-EventVPR
if [ $type = "event" ]; then 
    event=/home/taiyi/scratch/event_rendered/30fps
    output=/home/taiyi/scratch/NYC-Event-VPR_VG/NYC-Event-VPR_Event
elif [ $type = "reconstructed" ]; then 
    event=/home/taiyi/scratch/event_reconstructed/30fps
    output=/home/taiyi/scratch/NYC-Event-VPR_VG/NYC-Event-VPR_E2VID
elif [ $type = "rgb" ]; then 
    event=/home/taiyi/scratch/rgb_concatenated/30fps
    output=/home/taiyi/scratch/NYC-Event-VPR_VG/NYC-Event-VPR_RGB
fi
##############################################################################################################################################

# purge previous output directory 
rm -r $output 
mkdir $output 
echo "Purged previous dataset directories"

# process and create event dataset 
python /home/taiyi/scratch/event_dataset_generation_vg/main.py \
       --rdir $raw \
       --dir $output \
       --edir $event