import numpy as np
import cv2 as cv
import time
from datetime import datetime
import sys

def main(argv):
    # define variables
    cam_port = int(argv[1])
    width = 1280
    height = 720

    # open camera object
    cam = cv.VideoCapture(cam_port)
    cam.set(cv.CAP_PROP_FRAME_WIDTH, width)
    cam.set(cv.CAP_PROP_FRAME_HEIGHT, height)
    prev_frame_time, new_frame_time = time.time(), time.time()

    # graceful fail
    if not cam.isOpened():
        print('Cannot open camera...')
        exit()

    # main control loop
    while True:
        # obtain frame
        ret, frame = cam.read()
        if not ret:
            print('Failed to obtain frame')
            break

        # calculate fps
        new_frame_time = time.time()
        fps = 1 / (new_frame_time - prev_frame_time)
        prev_frame_time = new_frame_time
        # add annotations
        cv.putText(frame, 'Cam {} fps: {}'.format(cam_port, str(int(fps))), (30, 30), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv.putText(frame, 'Time: {}'.format(datetime.now()), (30, 50), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # display frame
        cv.imshow('frame', frame)

        # escape protocol
        k = cv.waitKey(1)
        if k%256 == 27: # ESC pressed
            print('Escaping...')
            break

    # cleanup
    cam.release()
    cv.destroyAllWindows()

if __name__ == '__main__':
    main(sys.argv)
