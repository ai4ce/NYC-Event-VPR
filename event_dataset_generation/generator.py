import pandas as pd
import geopy.distance
from time import time 
import numpy as np
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, wait 
from multiprocessing import cpu_count
import pickle
import cv2 as cv 
import os 

class Generator:
    # class constructor 
    def __init__(self, df: pd.DataFrame, ddir = '/home/taiyi/scratch/NYU-EventVPR-Event'):
        self.df = df
        self.ddir = ddir 
        self.dfq = None 
        self.gt = None 
        self.threshold = None 
        assert df is not None, 'New dataframe void'
        assert ddir is not None, 'Destination directory void'
        print('Dataframe object')
        print('Total entry count: {}'.format(self.df.shape[0]))
        print('Destination directory: {}'.format(self.ddir))
    
    # class string representation 
    def __str__(self) -> str:
        return None 
    
    # getter methods ###############################################################################################
    def get_query(self) -> pd.DataFrame:
        assert self.dfq is not None 
        print('{} query images returned'.format(self.dfq.shape[0]))
        print(self.dfq.head())
        return self.dfq
    
    def get_ref(self) -> pd.DataFrame:
        assert self.df is not None 
        print('{} ref images returned'.format(self.df.shape[0]))
        print(self.df.head())
        return self.df 
    
    def get_gt(self) -> np.ndarray:
        assert self.gt is not None 
        print('{}x{} ground truth numpy array returned'.format(self.gt.shape[0], self.gt.shape[1]))
        print(self.gt[0])
        return self.gt 
    
    def save_gt(self):
        assert self.gt is not None 
        self.pickle_compatible()
        self.gt_to_csv()

    # setter methods #########################################################################################
    def set_query(self, dfq: pd.DataFrame):
        assert dfq is not None 
        self.dfq = dfq 

    def set_ref(self, df: pd.DataFrame):
        assert df is not None 
        self.df = df
    
    # class methods ################################################################################################
    # filter only those above Sobel threshold, thus removing info sparse frames 
    def filter(self, sobel_threshold = 100):
        print('Applying Sobel operator...')
        self.df = self.df[self.df['Sobel'] > sobel_threshold]
        print('Sobel operation complete, resulting data entry: {}'.format(self.df.shape[0]))
        self.df.to_csv('peek/df_filtered.csv')

    # reduce total dataframe to a percentage of total rows, randomly sampled 
    def reduce(self, factor: float):
        print('Reducing dataframe to {:.2f}%...'.format(factor * 100))
        self.df = self.df.sample(frac=factor)
        print('Reduction complete, resulting data entry: {}'.format(self.df.shape[0]))
        self.df.to_csv('peek/df_reduced.csv')

    # sample a percentage of total dataframe, divide into query and reference (leftover after query is sampled)
    def sample(self, factor: float):
        # sample query images from reference images 
        self.dfq = self.df.sample(frac=factor).reset_index()
        print('Sampled {} query images from {} reference images'.format(self.dfq.shape[0], self.df.shape[0]))
        self.dfq.to_csv('peek/dfq.csv')
        # remove query images from reference images 
        self.df = self.df.drop(self.dfq['index']) # uncomment this to make dataset challenging 
        # shuffle reference images 
        self.df = self.df.sample(frac=1).reset_index()
        print('New reference image count: {}'.format(self.df.shape[0]))
        self.df.to_csv('peek/df.csv')

    # concurrently move selected images from query and reference to destination directory
    def move_imgs(self):
        start = time()

        print('Moving selected images into destination directory...')
        if not os.path.exists(self.ddir):
            os.mkdir(self.ddir)
        query_path = os.path.join(self.ddir, 'query')
        if not os.path.exists(query_path):
            os.mkdir(query_path)
        ref_path = os.path.join(self.ddir, 'ref')
        if not os.path.exists(ref_path):
            os.mkdir(ref_path)
        # divide up image moving tasks among CPU cores 
        with ThreadPoolExecutor() as executor:
            print('Started Thread Pool Executor...')
            futures = list()
            # move ref images 
            prev = 0
            for idx in range(self.df.shape[0] // cpu_count(), self.df.shape[0], self.df.shape[0] // cpu_count()):
                futures.append(
                    executor.submit(
                        self.img_io_thread,
                        self.df.iloc[prev:idx],
                        ref_path
                    )
                )
                prev = idx 
            futures.append(executor.submit(
                self.img_io_thread,
                self.df.iloc[prev:],
                ref_path
            ))
            # move query images 
            prev = 0
            for idx in range(self.dfq.shape[0] // cpu_count(), self.dfq.shape[0], self.dfq.shape[0] // cpu_count()):
                futures.append(
                    executor.submit(
                        self.img_io_thread,
                        self.dfq.iloc[prev:idx],
                        query_path
                    )
                )
                prev = idx 
            futures.append(executor.submit(
                self.img_io_thread,
                self.dfq.iloc[prev:],
                query_path
            ))
            # block until all futures finish
            wait(futures, return_when=concurrent.futures.ALL_COMPLETED)
            print('All concurrent futures have completed')
        print('Executor has shutdown')

        end = time()
        print('Time elapsed: {:.6f} hours'.format((end - start) / 3600.0))
        print('Time elapsed: {:.6f} minutes'.format((end - start) / 60.0))
        print('Time elapsed: {:.6f} seconds'.format((end - start) / 1.0))
        

    # generate ground truth array between query and reference images (multiprocessing)
    def compute_ground_truth(self, threshold = 25) -> np.ndarray:
        start = time()

        print('Computing ground truth with {} cores...'.format(cpu_count()))

        self.threshold = threshold
        assert threshold > 0, 'Fault tolenrance has to be positive'
        assert self.df is not None and self.dfq is not None, 'Need defined query and ref dataframes'

        # initialize ground truth numpy array
        self.gt = self.create_gt(self.dfq)
        
        # define multiprocessing program executor
        print('CPU core count: {}'.format(cpu_count()))
        executor = ProcessPoolExecutor()
        print('Started Process Pool Executor...')

        # divide task into equal chunks among all CPU threads 
        futures = list()
        assert self.dfq.shape[0] >= 100, 'Too few discrete tasks for {} threads'.format(cpu_count())
        # submit jobs to futures 
        prev = 0
        for idx in range(self.dfq.shape[0] // cpu_count(), self.dfq.shape[0], self.dfq.shape[0] // cpu_count()):
            futures.append(executor.submit(self.match_process, self.df, self.dfq, self.gt, prev, idx))
            prev = idx
        # block until all futures finish
        wait(futures, return_when=concurrent.futures.ALL_COMPLETED)
        print('All concurrent futures have completed')

        # merge resulting arrays based on index range
        for future in futures:
            self.gt[future.result()[1]:future.result()[2], :] = future.result()[0][future.result()[1]:future.result()[2], :]
        print('Concurrent futures merged')

        # shutdown executor
        executor.shutdown()
        print('Executor has shutdown')

        # iterate over remaining rows 
        self.match_process(self.df, self.dfq, self.gt, prev, self.df.shape[0])
        print('Remaining rows iterated')

        # save ground truth
        self.pickle_compatible()
        self.gt_to_csv()

        end = time()
        print('Time elapsed: {:.6f} hours'.format((end - start) / 3600.0))
        print('Time elapsed: {:.6f} minutes'.format((end - start) / 60.0))
        print('Time elapsed: {:.6f} seconds'.format((end - start) / 1.0))

    # helper functions ##################################################################################################
    # subprocess to be handled by an assigned CPU thread
    # upon completion, return partial array, start and end indices 
    # def match_process(self, df: pd.DataFrame, dfq: pd.DataFrame, gt: np.ndarray, start: int, end: int): # deprecated
    #     for row in dfq.iloc[start:end].itertuples():
    #         print('{}/{}'.format(row.index, df.shape[0] + dfq.shape[0] - 1))
    #         gt[row.Index][0] = row.Index # debug: row.Index -> row.index
    #         for r in df.itertuples():
    #             dist = self.calculate_gps_distance(
    #                 (row.Latitude, row.Longitude),
    #                 (r.Latitude, r.Longitude)
    #             )
    #             if dist < self.threshold:
    #                 gt[row.Index][1].append(r.Index) # debug: r.Index -> r.index 
    #     return gt, start, end
    
    # subprocess to be handled by an assigned CPU thread
    # upon completion, return partial array, start and end indices 
    # utilizes memoization for boosted efficiency
    def match_process(self, df: pd.DataFrame, dfq: pd.DataFrame, gt: np.ndarray, start: int, end: int):
        cache = dict() # cache for memoization (reduce exponential complexity)
        for row in dfq.iloc[start:end].itertuples():
            print('{}/{}'.format(row.index, df.shape[0] + dfq.shape[0] - 1))
            gt[row.Index][0] = row.Index # debug: row.Index -> row.index
            if cache.get(row.Timestamp) is None: # never seen before timestamp
                cache[row.Timestamp] = list()
                for r in df.itertuples():
                    dist = self.calculate_gps_distance(
                        (row.Latitude, row.Longitude),
                        (r.Latitude, r.Longitude)
                    )
                    if dist < self.threshold:
                        gt[row.Index][1].append(r.Index) # debug: r.Index -> r.index 
                        cache.get(row.Timestamp).append(r.Index)
            else: # timestamp encountered before 
                gt[row.Index][1] = cache.get(row.Timestamp)
        return gt, start, end

    # initialize ground truth numpy array according to dataframe dims 
    def create_gt(self, df: pd.DataFrame) -> np.ndarray:
        gt = np.zeros((df.shape[0], 2), dtype=np.ndarray)
        print(gt.shape)
        for i in range(gt.shape[0]):
            gt[i][0] = i 
            gt[i][1] = list()
        return gt 
    
    # calculate distance in meters between 2 GPS coordinates 
    # input: a(latitude, longitude), b(latitude, longitude)
    # output: distance in meters 
    def calculate_gps_distance(self, a: tuple, b: tuple) -> float:
        return geopy.distance.geodesic(a, b).meters
    
    # save ground truth numpy array as pickle protocol 2 compatible version 
    def pickle_compatible(self):
        np.save('peek/gt.npy', self.gt)
        try:
            with open('peek/gt.npy', 'rb') as handle:
                a = np.load(handle, allow_pickle=True)
            with open(os.path.join(self.ddir, 'ground_truth_new.npy'), 'wb') as handle:
                pickle.dump(a, handle, protocol=2)
        except:
            raise FileNotFoundError
        finally:
            print('Pickle protocol compatibility check')

    # visualize ground truth numpy array as a table with csv format 
    def gt_to_csv(self):
        try:
            pd.DataFrame(np.load(
                'peek/gt.npy', 
                allow_pickle = True
            )).to_csv(
                'peek/gt.csv',
                index = False, 
                header = False 
            )
        except:
            raise FileNotFoundError
        finally:
            print('Ground truth table saved')

    # subthread to be handled by main thread
    # move images to appropriate directories based on sub-dataframe given 
    def img_io_thread(self, df: pd.DataFrame, ddir: str):
        for row in df.itertuples():
            try:
                path1 = row.Path
                path2 = os.path.join(ddir, str(row.Index).zfill(7) + '.jpg')
                print('{} -> {}'.format(path1, path2))
                image = cv.imread(path1)
                cv.imwrite(path2, image)
            except:
                raise FileNotFoundError