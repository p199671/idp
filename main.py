from src import VideoConverter as VC
from src import ImagePreprocessing as im
from src import GStreamer as gst
from threading import Thread
import argparse
import os

if __name__ == '__main__':
    ''' Start Command Line Arguments Parser '''
    parser = argparse.ArgumentParser(description="Sensor Emulator")
    parser.add_argument('--image-path', required=True, type=str,
                        help='Specify path to the directory, where the images reside that should be converted into a '
                             'video.')
    parser.add_argument('--frame-rate', type=int, default = 25,
                        help='Specify the framerate (in fps) with which the video should be created out of the '
                             'images. If not given, the timestamps are used to calculate the framerate.')
    parser.add_argument('--rectify', type=str, default='False',
                        help='This options rectifies the image by performing Bayer '
                             'demosaicing and optionally undistorts the image (if '
                             'the camera model is given, see oxford dataset). True|False are valid arguments.')
    parser.add_argument('--resize-factor', default=1, type=float,
                        help='Specify the factor by which the image should be scaled up or down.')
    parser.add_argument('--upscale', type=str, default='False',
                        help='This options scales the images up by 4 using the max-image-resultion.'
                             'It is available under https://github.com/IBM/MAX-Image-Resolution-Enhancer.'
                             'True|False are valid arguments.')

    args = parser.parse_args()

    # Explicitly transform bool argument for option rectify since it is more comfortable in bash script
    if args.rectify in ["True", "true", "T", "t", "Yes", "yes", "Y", "y"]:
        args.rectify = True
    elif args.rectify in ["False", "false", "F", "f", "No", "no", "N", "n"]:
        args.rectify = False
    else:
        raise Exception("Wrong argument for option 'rectify'.")

    # Explicitly transform bool argument for option rectify since it is more comfortable in bash script
    if args.upscale in ["True", "true", "T", "t", "Yes", "yes", "Y", "y"]:
        args.upscale = True
    elif args.upscale in ["False", "false", "F", "f", "No", "no", "N", "n"]:
        args.upscale = False
    else:
        raise Exception("Wrong argument for option 'upscale'.")
    ''' End Command Line Arguments Parser'''

    # Assign command line options to variables
    path = args.image_path
    frame_rate = args.frame_rate
    rectify = args.rectify
    resize_factor = args.resize_factor
    upscale = args.upscale
    models_path = "./robotcar_dataset_sdk/models/"  # Path to models of sensors delivered with the oxford dataset

    # Delete and extract the sample to get intended starting conditions.
    # This part is just for development purposes and should be deleted later.
    os.system("rm -r sample_small")
    os.system("mkdir sample_small")
    os.system("tar -xvf sample_small.tar -C sample_small")
    os.system("rm ./out/*.mp4")



    # for path in paths:
    if rectify:
        print("Rectify images.")
        im.rectify_images(path, models_path)

    # im.interpolate_images("sample_small/mono_left/pic00.png", "sample_small/mono_left/pic01.png")

    if resize_factor != 1:
        print("Resize images with factor {}.".format(resize_factor))
        im.resize_image(path, factor=resize_factor)

    if upscale:
        im.upscale_image("sample_small/mono_right/")

    print("Convert images to video.")
    VC.convert_to_video(path, frame_rate=frame_rate, video_ext="mp4")
