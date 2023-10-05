#!/usr/bin/env bash

python3 demo_event_to_video.py \
    $1 \
    e2v.ckpt \
    --delta_t 40000 \
    --mode delta_t \
    --height_width 720 1280 \
    --video_path output.mp4