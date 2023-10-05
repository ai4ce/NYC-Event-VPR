#!/usr/bin/env bash
# batch 1 
fnames=("event_2023-02-14_15-06-33" \
        "event_2023-02-14_15-16-33" \
        "event_2023-02-14_15-26-33" \
        "event_2023-02-14_15-36-33" \
        "event_2023-02-14_15-46-33" \
        "event_2023-02-14_15-56-33" \
        "event_2023-02-14_16-06-33" \
        "event_2023-02-14_16-16-33" \
        "event_2023-02-14_16-26-33" \
        "event_2023-02-14_16-36-33")

input_path=/home/taiyi/repository2/data/sensor_data_2023-02-14_15-06-30/data_2023-02-14_15-06-33
output_path=/home/taiyi/repository2/data_processed/reconstruct/data_2023-02-14_15-06-33

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
e2v

# batch 2 
fnames=("event_2023-02-14_18-20-44" \
        "event_2023-02-14_18-30-44" \
        "event_2023-02-14_18-40-44" \
        "event_2023-02-14_18-50-44" \
        "event_2023-02-14_19-00-44" \
        "event_2023-02-14_19-10-44" \
        "event_2023-02-14_19-20-44" \
        "event_2023-02-14_19-30-44" \
        "event_2023-02-14_19-40-44" \
        "event_2023-02-14_19-50-44")

input_path=/home/taiyi/repository2/data/sensor_data_2023-02-14_18-20-40/data_2023-02-14_18-20-44
output_path=/home/taiyi/repository2/data_processed/reconstruct/data_2023-02-14_18-20-44

e2v

# batch 3
fnames=("event_2023-04-20_15-53-29" \
        "event_2023-04-20_16-03-29" \
        "event_2023-04-20_16-13-29" \
        "event_2023-04-20_16-23-29" \
        "event_2023-04-20_16-33-29" \
        "event_2023-04-20_16-43-29" \
        "event_2023-04-20_16-53-29" \
        "event_2023-04-20_17-03-29")

input_path=/home/taiyi/repository2/data/sensor_data_2023-04-20_15-53-26/data_2023-04-20_15-53-29
output_path=/home/taiyi/repository2/data_processed/reconstruct/data_2023-04-20_15-53-29

e2v

# batch 4
fnames=("event_2023-04-20_17-10-04" \
        "event_2023-04-20_17-20-04" \
        "event_2023-04-20_17-30-04" \
        "event_2023-04-20_17-40-04" \
        "event_2023-04-20_17-50-04" \
        "event_2023-04-20_18-00-04" \
        "event_2023-04-20_18-10-04" \
        "event_2023-04-20_18-20-04" \
        "event_2023-04-20_18-30-04")

input_path=/home/taiyi/repository2/data/sensor_data_2023-04-20_17-10-01/data_2023-04-20_17-10-04
output_path=/home/taiyi/repository2/data_processed/reconstruct/data_2023-04-20_17-10-04

e2v