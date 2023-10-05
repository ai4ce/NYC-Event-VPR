import pandas as pd
import glob
import os 
import argparse
import traceback
from aggregator import Aggregator
from synchrotron import Synchrotron
from generator import Generator

def main():
    # load dataframe 
    csv_path = os.path.join(args.rdir, 'sensor_data_*/GPS_data_*.csv')
    try:
        file_path = glob.glob(csv_path)
        print('GPS file count: {}'.format(len(file_path)))
        df = pd.concat(map(pd.read_csv, file_path), ignore_index = True)
        print('Total entry count: {}'.format(df.shape[0]))
        df.to_csv('peek/dataframe.csv')
    except:
        traceback.print_exc()
    # run synchrotron 
    if not args.synched:
        synchrotron = Synchrotron(args.edir, df)
        synchrotron.iterate_frames(args.framerate)
    # run aggregator
    aggregator = Aggregator(args.edir, df)
    aggregator.aggregate()
    df2 = aggregator.get_dataframe()
    # run generator 
    generator = Generator(df2, args.dir)
    generator.filter(args.sobel)
    if args.reduce < 1.0:
        generator.reduce(args.reduce)
    generator.sample(args.sample)
    generator.move_imgs()
    generator.compute_ground_truth(args.tolerance)
    generator.save_gt()

if __name__ == '__main__':
    # define command line arguments 
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--rdir', 
        required = False,
        type = str,
        default = '/home/taiyi/scratch/data',
        help = 'define input raw data directory (raw sensor readings)'
    )
    parser.add_argument(
        '--dir', 
        required = False,
        type = str,
        default = '/home/taiyi/scratch/NYU-EventVPR-Event',
        help = 'define output formatted data directory (compatible with VPR-Bench)'
    )
    parser.add_argument(
        '--edir',
        required = False,
        type = str,
        default = '/home/taiyi/scratch/event_rendered/30fps',
        help = 'define input event frame directory'
    )
    parser.add_argument(
        '--tolerance', 
        required = False,
        type = float,
        default = 25,
        help = 'define fault tolerance in meters, above which threshold is defined as a non-match'
    )
    parser.add_argument(
        '--sobel',
        required = False,
        type = float, 
        default = 100,
        help = 'define Sobel threshold (mean Sobel magnitude) below which is considered blank image and thus disgarded'
    )
    parser.add_argument(
        '--reduce',
        required = False,
        type = float, 
        default = 1.0,
        help = 'define reduce ratio (0 to 1) to drop excess images from dataframe'
    )
    parser.add_argument(
        '--sample',
        required = False,
        type = float,
        default = 0.1,
        help = 'define query sample ratio (0 to 1) to randomly sample query images from ref; ref then subtracts out sample query images'
    )
    parser.add_argument(
        '--framerate',
        required = False,
        type = float,
        default = 30,
        help = 'specify the framerate that the source event video is rendered; MUST MATCH EXACTLY!'
    )
    parser.add_argument(
        '--synched',
        required = False,
        type = int,
        default = 0,
        help = 'indicate if event frames are already synched. 0 is no. 1 is yes.'
    )
    # parse command line arguments 
    args = parser.parse_args()
    print(args)
    assert args.rdir is not None 
    assert args.dir is not None 
    assert args.edir is not None 
    assert args.tolerance > 0
    assert args.sobel >= 0 
    assert args.reduce > 0 and args.reduce <= 1
    assert args.sample > 0 and args.sample <= 1 
    assert args.framerate > 0
    assert args.synched == 0 or args.synched == 1
    main()