#!/usr/bin/env bash

e2v () {
    for fname in ${fnames[@]}; do 
        echo $fname;
        python3 demo_event_to_video.py \
            $input_path/$fname.raw \
            e2v.ckpt \
            --delta_t 40000 \
            --mode delta_t \
            --height_width 720 1280 \
            --video_path $output_path/$fname.mp4
    done 
}

rm -r /home/taiyi/scratch2/NYU-EventVPR_reconstructed_30fps/
python main.py