import pandas as pd
import glob
from time import time 
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor, wait 
import os 
import cv2 as cv 

class Aggregator:
    # class constructor 
    def __init__(self, dir: str, df: pd.DataFrame):
        self.dir = dir
        self.df = df 
        self.df2 = None 
        assert dir is not None, 'Event directory void'
        assert df is not None, 'Dataframe void'
        print('Filter object')
    
    # class string representation 
    def __str__(self) -> str:
        return None 
    
    # getter methods ###############################################################################################
    def get_dataframe(self) -> pd.DataFrame:
        return self.df2

    # class methods ################################################################################################
    # iterate over input event frames (various folders, various fps), 
    # correlate with original dataframe, filter out static frames (vehicle not moving)
    def aggregate(self):
        start = time()
        #########################################################################################
        self.df2 = pd.DataFrame(columns=['Latitude', 'Longitude', 'Timestamp', 'Hash', 'Path', 'Sobel'])
        self.iterate_folders()
        #########################################################################################
        end = time()
        print('Time elapsed: {:.6f} hours'.format((end - start) / 3600.0))
        print('Time elapsed: {:.6f} minutes'.format((end - start) / 60.0))
        print('Time elapsed: {:.6f} seconds'.format((end - start) / 1.0))

    # helper functions ##################################################################################################
    # use concurrency to iterate over all folders containing event frames (previously synchronized)
    def iterate_folders(self):
        with ProcessPoolExecutor() as executor:
            print('Started Process Pool Executor...')
            futures = list()
            folder_path = glob.glob(os.path.join(self.dir, 'event_*'))
            print('{} event data directories found'.format(len(folder_path)))
            # iterate over event folders, iterate frames: first pass 
            for folder in folder_path:
                futures.append(
                    executor.submit(
                        self.iterate_frames,
                        folder
                    )
                )
            # block until all futures finish
            wait(futures, return_when=concurrent.futures.ALL_COMPLETED)
            print('All concurrent futures have completed')
            # merge concurrent futures 
            for future in futures:
                self.df2 = pd.concat([
                    self.df2, 
                    future.result()
                ], ignore_index = True
                )
            print('Concurrent futures merged')
        print('Executor has shutdown')
        self.df2.to_csv('peek/df_aggregated.csv')

    # concurrent thread: iterate over all frames in folder, correlate with original datadframe, return new subframe 
    def iterate_frames(self, folder: str) -> pd.DataFrame:
        print(folder)
        df2 = pd.DataFrame(columns=['Latitude', 'Longitude', 'Timestamp', 'Hash', 'Path', 'Sobel'])
        for img in os.listdir(folder):
            print(img)
            # extract timestamp and hash string 
            tokens = img.split('_')
            timestamp = '_'.join(tokens[1:4])
            hash = tokens[4].split('.')[0]
            # locate corresponding rows in original dataframe 
            row = self.df[self.df['Timestamp'] == timestamp]
            # open image and calculate mean Sobel operator (x and y) magnitude 
            img_path = os.path.join(folder, img)
            try:
                image = cv.imread(img_path)
            except:
                raise FileNotFoundError
            sobelx = cv.Sobel(image, cv.CV_64F, 1, 0, ksize = 5)
            sobely = cv.Sobel(image, cv.CV_64F, 0, 1, ksize = 5)
            sobel = cv.mean(cv.mean(cv.magnitude(sobelx, sobely)))[0]
            # add row data to new dataframe 
            df2 = pd.concat([
                    df2,
                    pd.DataFrame({
                        'Latitude': row['Latitude'],
                        'Longitude': row['Longitude'],
                        'Timestamp': timestamp,
                        'Hash': hash,
                        'Path': img_path,
                        'Sobel': sobel
                    }
                )],
                ignore_index = True
            )
        return df2 