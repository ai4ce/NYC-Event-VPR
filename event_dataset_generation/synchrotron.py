import pandas as pd
import glob
from time import time 
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor, wait 
import os 
from pathlib import Path
from datetime import datetime
from datetime import timedelta
import cv2 as cv 
import random

class Synchrotron:
    # class constructor 
    def __init__(self, dir: str, df: pd.DataFrame):
        self.dir = dir
        self.df = df 
        assert dir is not None, 'Event directory void'
        assert df is not None, 'Dataframe void'
        print('Synchrotron object')
    
    # class string representation 
    def __str__(self) -> str:
        return None 

    # class methods ################################################################################################
    # iterate over event frames, synch timestamps
    def iterate_frames(self, framerate = 30):
        start = time()

        folder_path = glob.glob(os.path.join(self.dir, 'event_*'))
        print('{} event data directories found'.format(len(folder_path)))
        # initialize executor 
        with ProcessPoolExecutor() as executor:
            print('Started Process Pool Executor...')
            futures = list()
            # iterate through all event frame folders 
            for folder in folder_path:
                futures.append(
                    executor.submit(
                        self.match_timestamp,
                        folder,
                        self.df,
                        framerate
                    )
                )
            # block until all futures finish
            wait(futures, return_when=concurrent.futures.ALL_COMPLETED)
            print('All concurrent futures have completed')
        print('Executor has shutdown')

        end = time()
        print('Time elapsed: {:.6f} hours'.format((end - start) / 3600.0))
        print('Time elapsed: {:.6f} minutes'.format((end - start) / 60.0))
        print('Time elapsed: {:.6f} seconds'.format((end - start) / 1.0))

    # helper functions ##################################################################################################
    # match image to timestamp, then move image 
    def match_timestamp(self, folder: str, df: pd.DataFrame, framerate: float):
        # calculate folder time at index 0 point 
        t0 = datetime.strptime(
            '_'.join(Path(folder).stem.split('_')[1:]),
            '%Y-%m-%d_%H-%M-%S'
        )
        # iterate over all images in folder 
        for img in os.listdir(folder):
            diff_min = timedelta.max
            timestamp_min = None 
            # calculate image timestamp based on folder time, image index, and sampling frame rate 
            img_time = t0 + timedelta(
                seconds = (int(img.split('.')[0]) - 1) / framerate # images are 1-indexed, hence -1
            )
            # iterate over dataframe for timestamp matches 
            for row in df.itertuples():
                # extract row timestamp
                timestamp = datetime.strptime(
                    row.Timestamp,
                    '%Y-%m-%d_%H-%M-%S_%f'
                )
                # calculate time difference between image and row, record mininum time difference
                diff = abs(timestamp - img_time)
                if diff < diff_min:
                    timestamp_min = row.Timestamp
                    diff_min = diff 
            # display matched event frame to timestamp 
            print('Event frame: {} <--> Matched timestamp: {}'.format(os.path.join(Path(folder).stem, img), timestamp_min))

            # use match to move image 
            try:
                img_path = os.path.join(folder, img)
                image = cv.imread(img_path)
                os.remove(img_path)
                cv.imwrite(os.path.join(folder, 'frame_' + timestamp_min + '_' + '%032x' % random.getrandbits(128) + '.jpg'), image)
            except:
                raise FileNotFoundError