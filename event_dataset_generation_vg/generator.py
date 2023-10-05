import utm 
import cv2 as cv 
from time import time 
import pandas as pd 
import os 

class Generator:
    def __init__(self, dir: str, df: pd.DataFrame):
        self.dir = dir 
        self.df = df 
        self.train = None 
        self.val = None 
        self.test = None
        self.train_dir = None 
        self.val_dir = None 
        self.test_dir = None  
        print('Generator created')

    def generate(self):
        start = time()
        #########################################################################################
        self.create_folders()
        self.slice()
        self.format()
        #########################################################################################
        end = time()
        print('Time elapsed: {:.6f} hours'.format((end - start) / 3600.0))
        print('Time elapsed: {:.6f} minutes'.format((end - start) / 60.0))
        print('Time elapsed: {:.6f} seconds'.format((end - start) / 1.0))

# helper functions ##################################################################################################
    def create_folders(self):
        if not os.path.exists(os.path.join(self.dir, 'images')):
            os.mkdir(os.path.join(self.dir, 'images'))
            self.dir = os.path.join(self.dir, 'images')
            print('New dir: {}'.format(self.dir))
        self.train_dir = os.path.join(self.dir, 'train')
        self.val_dir = os.path.join(self.dir, 'val')
        self.test_dir = os.path.join(self.dir, 'test')
        if not os.path.exists(self.train_dir):
            os.mkdir(self.train_dir)
            self.create_subfolders(self.train_dir)
            print('New train dir: {}'.format(self.train_dir))
        if not os.path.exists(self.val_dir):
            os.mkdir(self.val_dir)
            self.create_subfolders(self.val_dir)
            print('New val dir: {}'.format(self.val_dir))
        if not os.path.exists(self.test_dir):
            os.mkdir(self.test_dir)
            self.create_subfolders(self.test_dir)
            print('New test dir: {}'.format(self.test_dir))

    def create_subfolders(self, dir):
        if not os.path.exists(os.path.join(dir, 'database')):
            os.mkdir(os.path.join(dir, 'database'))
        if not os.path.exists(os.path.join(dir, 'queries')):
            os.mkdir(os.path.join(dir, 'queries'))

    def slice(self):
        # sample train dataset 
        self.train = self.df.sample(frac=0.4).reset_index()
        self.df = self.df.drop(self.train['index'])
        self.train.to_csv('peek/train.csv')

        # sample val dataset 
        self.val = self.df.sample(frac=0.5).reset_index()
        self.df = self.df.drop(self.val['index'])
        self.val.to_csv('peek/val.csv')

        # sample test dataset 
        self.test = self.df.sample(frac=1.0).reset_index()
        self.test.to_csv('peek/test.csv')

    def format(self):
        # split train dataset
        # queries
        self.train_query = self.train.sample(frac=0.1).reset_index()
        self.train_query.to_csv('peek/train_query.csv')
        self.move_imgs(self.train_query, os.path.join(self.train_dir, 'queries'))
        # database 
        self.train_database = self.train.drop(self.train_query['level_0']).reset_index()
        self.train_database.to_csv('peek/train_database.csv')
        self.move_imgs(self.train_database, os.path.join(self.train_dir, 'database'))

        # split val dataset 
        # queries 
        self.val_query = self.val.sample(frac=0.1).reset_index()
        self.val_query.to_csv('peek/val_query.csv')
        self.move_imgs(self.val_query, os.path.join(self.val_dir, 'queries'))
        # database 
        self.val_database = self.val.drop(self.val_query['level_0']).reset_index()
        self.val_database.to_csv('peek/val_database.csv')
        self.move_imgs(self.val_database, os.path.join(self.val_dir, 'database'))

        # split test dataset 
        # queries 
        self.test_query = self.test.sample(frac=0.1).reset_index()
        self.test_query.to_csv('peek/test_query.csv')
        self.move_imgs(self.test_query, os.path.join(self.test_dir, 'queries'))
        # database 
        self.test_database = self.test.drop(self.test_query['level_0']).reset_index()
        self.test_database.to_csv('peek/test_database.csv')
        self.move_imgs(self.test_database, os.path.join(self.test_dir, 'database'))

    def move_imgs(self, df: pd.DataFrame, dir: str):
        for r in df.itertuples():
            # calculate utm coordinates 
            coordinates = utm.from_latlon(r.Latitude, r.Longitude)
            # format new image path 
            path = '@' + '@'.join([
                str(coordinates[0]),
                str(coordinates[1]),
                str(coordinates[2]),
                str(coordinates[3]),
                str(r.Latitude),
                str(r.Longitude),
                str(),
                str(),
                str(r.Heading),
                str(),
                str(),
                str(),
                str(r.Timestamp),
                str(r.Hash),
                '.jpg'
            ])
            path = os.path.join(dir, path)
            print('{} -> {}'.format(r.Path, path))
            # move image 
            try:
                image = cv.imread(r.Path)
                cv.imwrite(path, image)
            except:
                raise FileNotFoundError
