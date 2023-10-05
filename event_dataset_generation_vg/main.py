import pandas as pd
import glob
import os 
import argparse
import traceback
from aggregator import Aggregator
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
    # run aggregator
    aggregator = Aggregator(args.edir, df)
    aggregator.aggregate()
    df2 = aggregator.get_dataframe()
    # run generator 
    generator = Generator(args.dir, df2)
    generator.generate()
 
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
        default = '/home/taiyi/scratch/NYC-Event-VPR_VG/NYC-Event-VPR_Event',
        help = 'define output formatted data directory (compatible with VG framework)'
    )
    parser.add_argument(
        '--edir',
        required = False,
        type = str,
        default = '/home/taiyi/scratch/event_rendered/30fps',
        help = 'define input event frame directory'
    )
    # parse command line arguments 
    args = parser.parse_args()
    print(args)
    assert args.rdir is not None 
    assert args.dir is not None 
    assert args.edir is not None 
    main()