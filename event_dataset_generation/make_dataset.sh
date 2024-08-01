#!/bin/bash

# define hyperparams
fault_tolerance=15
sobel_threshold=0
sample_fps=1
type="event" # choices: event, reconstructed, rgb
light="null" # choices: day, night, null

#############################################################################################################################################
# define paths 
raw=/home/taiyi/scratch2/NYU-EventVPR
if [ $type = "event" ]; then 
    event=/home/taiyi/scratch/event_rendered/30fps
    output=/home/taiyi/scratch/NYU-EventVPR_VPR-Bench/event_"$fault_tolerance"m_"$sobel_threshold"sobel_"$sample_fps"fps
    files="/mnt/scratch2/NYU-EventVPR_rendered_30fps/data_*/event_*.avi"
    if [ $light = "day" ]; then 
        readarray -t a < paths/event_day.txt
        files="${a[@]}"
        output=/home/taiyi/scratch/NYU-EventVPR_VPR-Bench/event_"$fault_tolerance"m_"$sobel_threshold"sobel_"$sample_fps"fps_day
    elif [ $light = "night" ]; then 
        readarray -t a < paths/event_night.txt 
        files="${a[@]}"
        output=/home/taiyi/scratch/NYU-EventVPR_VPR-Bench/event_"$fault_tolerance"m_"$sobel_threshold"sobel_"$sample_fps"fps_night
    fi 
elif [ $type = "reconstructed" ]; then 
    event=/home/taiyi/scratch/event_reconstructed/30fps
    output=/home/taiyi/scratch/NYU-EventVPR_VPR-Bench/reconstructed_"$fault_tolerance"m_"$sobel_threshold"sobel_"$sample_fps"fps
    files="/mnt/scratch2/NYU-EventVPR_reconstructed_30fps/data_*/event_*.mp4"
    if [ $light = "day" ]; then 
        readarray -t a < paths/reconstructed_day.txt
        files="${a[@]}"
        output=/home/taiyi/scratch/NYU-EventVPR_VPR-Bench/reconstructed_"$fault_tolerance"m_"$sobel_threshold"sobel_"$sample_fps"fps_day
    elif [ $light = "night" ]; then 
        readarray -t a < paths/reconstructed_night.txt 
        files="${a[@]}"
        output=/home/taiyi/scratch/NYU-EventVPR_VPR-Bench/reconstructed_"$fault_tolerance"m_"$sobel_threshold"sobel_"$sample_fps"fps_night
    fi 
elif [ $type = "rgb" ]; then 
    event=/home/taiyi/scratch/rgb_concatenated/30fps
    output=/home/taiyi/scratch/NYU-EventVPR_VPR-Bench/rgb_"$fault_tolerance"m_"$sobel_threshold"sobel_"$sample_fps"fps
    files="/mnt/scratch2/NYU-EventVPR_rgb_30fps/data_*/event_*.mp4"
    if [ $light = "day" ]; then 
        readarray -t a < paths/rgb_day.txt
        files="${a[@]}"
        output=/home/taiyi/scratch/NYU-EventVPR_VPR-Bench/rgb_"$fault_tolerance"m_"$sobel_threshold"sobel_"$sample_fps"fps_day
    elif [ $light = "night" ]; then 
        readarray -t a < paths/rgb_night.txt 
        files="${a[@]}"
        output=/home/taiyi/scratch/NYU-EventVPR_VPR-Bench/rgb_"$fault_tolerance"m_"$sobel_threshold"sobel_"$sample_fps"fps_night
    fi 
fi
##############################################################################################################################################

# print hyperparams 
echo $fault_tolerance
echo $sobel_threshold
echo $sample_fps
echo $type
echo $light

# print variables 
echo $raw
echo $event 
echo $output
echo $files

# purge previous output directory 
rm -r $event
rm -r $output 
mkdir $event 
echo "Purged previous dataset directories"

########################################################
# ffmpeg frame generation 
# calculate sampling rate for 30fps source videos
framerate=$(($sample_fps * 1))

# iterate over all video files 
for file in $files
do 
    # extract extract and remove extension
    filename=$(basename -- "$file")
    filename=${filename%.*}
    echo "Processing $file"
    
    # create output frame directory for targeted event video 
    mkdir $event/$filename/
    echo "Output directory $event/$filename"

    # sample event video into frames 
    ffmpeg -hwaccel cuda -i $file -vf fps=$framerate $event/$filename/%07d.jpg 
done 
########################################################

# process and create event dataset 
python /home/taiyi/scratch/event_dataset_generation/main.py \
       --rdir $raw \
       --dir $output \
       --edir $event \
       --tolerance $fault_tolerance \
       --sobel $sobel_threshold \
       --reduce 1.0 \
       --sample 0.1 \
       --framerate $sample_fps \
       --synched 0