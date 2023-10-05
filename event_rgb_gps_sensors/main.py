from metavision_sdk_core import PeriodicFrameGenerationAlgorithm
from metavision_sdk_ui import EventLoop, BaseWindow, Window, UIAction, UIKeyEvent
from metavision_core.event_io import EventsIterator
from metavision_core.event_io.raw_reader import initiate_device
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor, wait
from multiprocessing import cpu_count
from datetime import datetime
from datetime import timedelta
import cv2 as cv
import traceback
import numpy as np
from ublox_gps import UbloxGps
import serial
import traceback
import glob
import sys
import os
import math

# global variables: BE CAREFUL! COULD PERMANENTLY DAMAGE SENSOR!
bias_fo = -35
bias_hpf = 30
bias_diff_off = 40
bias_diff_on = 40
bias_refr = 0
band_min, band_max = 50, 500
trail_threshold = 100000
erc_max = 10000000

# define program behavior
event_time_limit = 10 # minutes; define maximum time limit for raw event data file in order to reduce file size 

# global directory path
folder_path = 'sensor_data_{}'.format(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))

# search for camera port
def find_port():
    ports = glob.glob('/dev/ttyACM[0-9]*')
    res = list()
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            res.append(port)
        except:
            pass
    return res[0]

# create GPS object
def gps_object():
    port = serial.Serial(
        find_port(),
        baudrate = 38400,
        timeout = 1
    )
    return UbloxGps(port), port

# check runtime against start_time, return updated hour value
def check_runtime(start_time, hours_prev):
    hours_elapsed = (datetime.now() - start_time).total_seconds() / 60.0**2
    if math.floor(hours_elapsed) > hours_prev:
        print('{} hours elapsed'.format(math.floor(hours_elapsed)))
        return hours_elapsed
    else:
        return hours_prev

def event_block(t0):
    t1 = datetime.now()
    if t1 > t0 + timedelta(minutes = event_time_limit):
        return t1, True 
    return t0, False 

# dedicated CPU thread for RGB and GPS data processing
def rgb_gps_thread(port):
    print('RGB GPS thread has began')
    # define variables
    cam_port = port
    width = 1280
    height = 720
    hours_prev = 0
    start_time = datetime.now()

    # open camera object
    cam = cv.VideoCapture(cam_port)
    cam.set(cv.CAP_PROP_FRAME_WIDTH, width)
    cam.set(cv.CAP_PROP_FRAME_HEIGHT, height)

    # graceful fail
    if not cam.isOpened():
        print('Cannot open camera...')
        exit()

    # open gps object
    try:
        gps, port = gps_object()
    except:
        print(traceback.format_exc())

    try:
        # obtain start time string
        start_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        # open gps csv file
        f = open('{}/GPS_data_{}.csv'.format(folder_path, start_str), 'w')
        f.write('Longitude,Latitude,HeadMotion,Timestamp\n')
        # create image directory
        if not os.path.exists('{}/img_{}'.format(folder_path, start_str)):
            os.mkdir('{}/img_{}'.format(folder_path, start_str))
        # main control loop
        while True:
            # check runtime
            hours_prev = check_runtime(start_time, hours_prev)
            # obtain frame
            ret, frame = cam.read()
            if not ret:
                print('Failed to obtain frame')
                break
            # obtain gps coordinates
            geo = gps.geo_coords()
            # obtain current time string
            time_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S_%f')
            # save frame
            cv.imwrite('{}/img_{}/frame_{}.jpg'.format(folder_path, start_str, time_str), frame)
            # save coordinates
            f.write('{},{},{},{}\n'.format(
                geo.lon,
                geo.lat,
                geo.headMot,
                time_str
            ))
            # display dummy frame
            dummy = np.zeros((200, 400))
            cv.imshow('ELP RGB Camera', dummy)
            # escape protocol
            k = cv.waitKey(1)
            if k%256 == 27: # ESC pressed
                print('Escaping RGB window...')
                break
    except:
        print(traceback.format_exc())
    finally:
        f.close()
        cv.destroyAllWindows()
        cam.release()
        port.close()
        print('RGB GPS thread has ended')

# dedicated CPU thread for event data processing
def event_thread():
    print('Event thread has began')
    # create HAL device
    device = initiate_device(path = '')

    # tune bias within safe ranges
    bias = device.get_i_ll_biases()
    assert bias_fo >= -35 and bias_fo <= 55, 'bias_fo safe range: (-35, 55)'
    bias.set('bias_fo', bias_fo)
    assert bias_hpf >= 0 and bias_hpf <= 120, 'bias_hpf safe range: (0, 120)'
    bias.set('bias_hpf', bias_hpf)
    assert bias_diff_off >= -35 and bias_diff_off <= 190, 'bias_diff_off safe range: (-35, 190)'
    bias.set('bias_diff_off', bias_diff_off)
    assert bias_diff_on >= -85 and bias_diff_on <= 140, 'bias_diff_on safe range: (-85, 140)'
    bias.set('bias_diff_on', bias_diff_on)
    assert bias_refr >= -20 and bias_refr <= 235, 'bias_refr safe range: (-20, 235)'
    bias.set('bias_refr', bias_refr)
    print('IMX636ES sensor bias:', bias.get_all_biases())

    # AFK: anti-flicker
    anti_flicker = device.get_i_antiflicker_module()
    anti_flicker.enable()
    anti_flicker.set_frequency_band(band_min, band_max, True) # Hz

    # STC/Trail: event trail filter
    noise_filter = device.get_i_noisefilter_module()
    noise_filter.enable_trail(trail_threshold) # microseconds; 100ms

    # ERC: event rate controller
    erc = device.get_i_erc()
    erc.enable(True)
    assert erc_max > 0, 'erc_max must be positive'
    erc.set_cd_event_rate(erc_max)
    print('Event rate controller status:', erc.is_enabled())
    print('Event rate limit (Ev/s):', erc.get_cd_event_rate())

    # create event stream object
    stream = device.get_i_events_stream()

    # create iterator
    iterator = EventsIterator.from_device(device = device, delta_t=1e3)
    height, width = iterator.get_size()  # Camera Geometry

    # Window - Graphical User Interface
    with Window(title="Prophesee EVK4 HD Sony IMX636ES Event Camera", width=width, height=height, mode=BaseWindow.RenderMode.BGR) as window:
        # define keyboard callback
        def keyboard_cb(key, scancode, action, mods):
            if action != UIAction.RELEASE:
                return
            if key == UIKeyEvent.KEY_ESCAPE or key == UIKeyEvent.KEY_Q:
                window.set_close_flag()

        window.set_keyboard_callback(keyboard_cb)

        # Event Frame Generator
        event_frame_gen = PeriodicFrameGenerationAlgorithm(width, height, fps = 30.0)

        # define on frame callback
        def on_cd_frame_cb(ts, cd_frame):
            nonlocal display_str
            cv.putText(cd_frame, display_str, (0, 10), cv.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0))
            window.show(cd_frame)

        event_frame_gen.set_output_callback(on_cd_frame_cb)

        # obtain start time string
        start_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        # create event directory 
        if not os.path.exists('{}/data_{}'.format(folder_path, start_str)):
            os.mkdir('{}/data_{}'.format(folder_path, start_str))
        # begin event log
        t0 = datetime.now()
        stream.log_raw_data('{}/data_{}/event_{}.raw'.format(folder_path, start_str, t0.strftime('%Y-%m-%d_%H-%M-%S')))

        # Process event batches
        for evs in iterator:
            # block size check; create new save file if over size limit 
            t0, over = event_block(t0)
            if over:
                stream.stop_log_raw_data()
                stream.log_raw_data('{}/data_{}/event_{}.raw'.format(folder_path, start_str, t0.strftime('%Y-%m-%d_%H-%M-%S')))
                print('{} minute event block saved at {}'.format(event_time_limit, t0))
            # calculate event rate
            display_str = "Rate : {:.2f}Mev/s".format(evs.size * 1e-3)
            # Dispatch system events to the window
            EventLoop.poll_and_dispatch()
            event_frame_gen.process_events(evs)
            # callback flag
            if window.should_close():
                print('Escaping event window...')
                break

    # stop event log
    stream.stop_log_raw_data()
    print('Event thread has ended')

def main(argv):
    try: 
        int(argv[1])
    except:
        print('Please specify RGB camera port')
        exit()

    # create directory to save data for this run
    print('Creating data directory {}'.format(folder_path))
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)

    # define multiprocessing program executor
    print('CPU core count: {}'.format(cpu_count()))
    executor = ProcessPoolExecutor(cpu_count() - 1)
    print('Started Process Pool Executor...')

    # pass functions to executor to parallel run
    futures = list()
    futures.append(executor.submit(event_thread))
    futures.append(executor.submit(rgb_gps_thread, int(argv[1])))
    done, not_done = wait(futures, return_when = concurrent.futures.ALL_COMPLETED)
    print('All concurrent futures have completed')

    # shutdown executor
    executor.shutdown()
    print('Executor has shutdown')

if __name__ == '__main__':
    main(sys.argv)
