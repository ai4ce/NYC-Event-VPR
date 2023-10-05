from metavision_sdk_core import PeriodicFrameGenerationAlgorithm
from metavision_sdk_ui import EventLoop, BaseWindow, Window, UIAction, UIKeyEvent
from metavision_core.event_io import EventsIterator
from metavision_core.event_io.raw_reader import initiate_device
from datetime import datetime
import cv2 as cv
import traceback

def parse_args():
    import argparse
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Metavision SDK Get Started sample.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-i', '--input-raw-file', dest='input_path', default="",
        help="Path to input RAW file. If not specified, the live stream of the first available camera is used. "
        "If it's a camera serial number, it will try to open that camera instead.")
    args = parser.parse_args()
    return args


def main():
    """ Main """
    args = parse_args()

    # create HAL device
    device = initiate_device(path = args.input_path)

    # tune bias
    device.get_i_ll_biases().set('bias_fo', -35)
    device.get_i_ll_biases().set('bias_hpf', 30)
    device.get_i_ll_biases().set('bias_diff_off', 40)
    device.get_i_ll_biases().set('bias_diff_on', 40)
    print(device.get_i_ll_biases().get_all_biases())

    # AFK: anti-flicker
    device.get_i_antiflicker_module().enable()
    device.get_i_antiflicker_module().set_frequency_band(50, 500, True)

    # STC/Trail: event trail filter
    device.get_i_noisefilter_module().enable_trail(100000)

    # ERC: event rate controller
    device.get_i_erc().enable(True)
    device.get_i_erc().set_cd_event_rate(10000000)
    # print(device.get_i_erc().is_enabled())
    # print(device.get_i_erc().get_cd_event_rate())

    # create iterator
    iterator = EventsIterator.from_device(device = device, delta_t=1e3)
    height, width = iterator.get_size()  # Camera Geometry

    # Window - Graphical User Interface
    with Window(title="Metavision SDK Get Started", width=width, height=height, mode=BaseWindow.RenderMode.BGR) as window:
        # define callback
        def keyboard_cb(key, scancode, action, mods):
            if action != UIAction.RELEASE:
                return
            if key == UIKeyEvent.KEY_ESCAPE or key == UIKeyEvent.KEY_Q:
                window.set_close_flag()

        window.set_keyboard_callback(keyboard_cb)

        # Event Frame Generator
        event_frame_gen = PeriodicFrameGenerationAlgorithm(width, height, fps = 30.0)

        def on_cd_frame_cb(ts, cd_frame):
            nonlocal display_str
            # cv.putText(cd_frame, "Timestamp: " + str(ts), (0, 10), cv.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0))
            cv.putText(cd_frame, display_str, (0, 10), cv.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0))
            window.show(cd_frame)

        event_frame_gen.set_output_callback(on_cd_frame_cb)

        # Process events
        for evs in iterator:
            display_str = "Rate : {:.2f}Mev/s".format(evs.size * 1e-3)

            # Dispatch system events to the window
            EventLoop.poll_and_dispatch()

            event_frame_gen.process_events(evs)

            if window.should_close():
                break

if __name__ == "__main__":
    main()
