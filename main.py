from time import sleep

from src import VideoConverter as vc
from src import ImagePreprocessing as im
from src import GStreamer as gst
from threading import Thread
import argparse
import os

if __name__ == '__main__':
    # # Parse command line arguments
    # parser = argparse.ArgumentParser(description="")
    # parser.add_argument('--image_path', required=True, help='Specify path to the directory, where the images reside that should be converted into a video.')
    # parser.add_argument('--frame_rate', type=int, help='Specify the framerate (in fps) with which the video should be created out of the images. If not given, the timestamps are used to calculate the framerate.')
    # parser.add_argument('--rectify', action='store_true', help='This options rectifies the image by performing Bayer '
    #                                                            'demosaicing and optionally undistorts the image (if '
    #                                                            'the camera model is given, see oxford dataset)')
    # parser.add_argument('--resize', type=int, help='Specify the factor by which the image should be scaled up or down.')
    # args = parser.parse_args()

    # # Delete and extract the sample to get intended starting conditions.
    # # This part is just for development purposes and should be deleted later.
    # os.system("rm -r sample_small")
    # os.system("mkdir sample_small")
    # os.system("tar -xvf sample_small.tar -C sample_small")
    # os.system("rm ./out/*.mp4")
    #
    # # Set options.
    # # These options should be later transferred into a config file or to command line options
    # # and are just for development purposes.
    # paths = ['./sample_small/mono_left/', './sample_small/mono_rear/', './sample_small/mono_right/']
    # models_path = "./robotcar_dataset_sdk/models/"
    # frame_rate = 25
    # rectify = True
    # resize_factor = 1
    #
    # for path in paths:
    #     if rectify: im.rectify_images(path, models_path)
    #     vc.convert_to_video(path, frame_rate=frame_rate, video_ext="mp4")

    # im.interpolate_images("sample_small/mono_left/pic00.png", "sample_small/mono_left/pic01.png")
    # im.resize_image("sample_small/mono_left/", factor=5)

    # im.upscale_image("sample_small/mono_right/")

