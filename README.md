# NYC-Event-VPR: A Large-Scale High-Resolution Event-Based Visual Place Recognition Dataset in Dense Urban Environments 
[Taiyi Pan](http://www.taiyipan.org), [Chao Chen*](https://joechencc.github.io), [Yiming Li*](https://scholar.google.com/citations?user=i_aajNoAAAAJ), [Chen Feng](https://scholar.google.com/citations?user=YeG8ZM0AAAAJ)

New York University, Tandon School of Engineering

## Abstract 
Visual place recognition (VPR) enables autonomous robots to identify previously visited locations, which contributes to tasks like simultaneous localization and mapping (SLAM). VPR faces challenges such as accurate image neighbor retrieval and appearance change in scenery.

Event cameras, also known as dynamic vision sensors, are a new sensor modality for VPR and offer a promising solution to the challenges with their unique attributes: high temporal resolution (1MHz clock), ultra-low latency (in μs), and high dynamic range (>120dB). These attributes make event cameras less susceptible to motion blur and more robust in variable lighting conditions, making them suitable for addressing VPR challenges. However, the scarcity of event-based VPR datasets, partly due to the novelty and cost of event cameras, hampers their adoption.

To fill this data gap, our paper introduces the NYC-Event-VPR dataset to the robotics and computer vision communities, featuring the Prophesee IMX636 HD event sensor (1280x720 resolution), combined with RGB camera and GPS module. It encompasses over 13 hours of geotagged event data, spanning 260+ kilometers across New York City, covering diverse lighting and weather conditions, day/night scenarios, and multiple visits to various locations.

Furthermore, our paper employs the VPR-Bench framework to conduct generalization performance assessments, promoting innovation in event-based VPR and its integration into robotics applications.