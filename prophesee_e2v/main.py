import subprocess
import os 
import glob 

def run(input: str, output: str):
    subprocess.run([
        'python',
        'demo_event_to_video.py',
        input,
        'e2v.ckpt',
        '--delta_t',
        '40000',
        '--mode',
        'delta_t',
        '--height_width',
        '720',
        '1280',
        '--video_path',
        output
    ])

def create_map(files: list, files2: list, dir: str) -> dict:
    if not os.path.exists(dir):
        os.mkdir(dir)
    map = dict()
    for file in files:
        tokens = os.path.basename(file).split('.')[0].split('_')
        timestamp = '_'.join(tokens[1:])
        fname = os.path.join(dir, 'data_' + timestamp)
        if not os.path.exists(fname):
            os.mkdir(fname)
        output = os.path.join(fname, 'event_' + timestamp + '.mp4')
        map[file] = output
        
    for file in files2:
        fname = os.path.join(dir, file.split('/')[-2])
        if not os.path.exists(fname):
            os.mkdir(fname)
        tokens = os.path.basename(file).split('.')[0].split('_')
        timestamp = '_'.join(tokens[1:])
        output = os.path.join(fname, 'event_' + timestamp + '.mp4')
        map[file] = output

    print(len(map))
    return map 

def main():
    # define input path 
    rdir = '/home/taiyi/scratch2/NYU-EventVPR'
    files = glob.glob(os.path.join(rdir, 'sensor_data_*/data_*.raw'))
    files2 = glob.glob(os.path.join(rdir, 'sensor_data_*/data_*/event_*.raw'))
    print(len(files) + len(files2))

    # define output path 
    dir = '/home/taiyi/scratch2/NYU-EventVPR_reconstructed_30fps'

    # create map 
    map = create_map(files, files2, dir)

    # iterate over files and reconstruct event data into frames 
    for file in (files + files2):
        print('{} ---> {}'.format(file, map.get(file)))
        run(file, map.get(file))

if __name__ == '__main__':
    main()