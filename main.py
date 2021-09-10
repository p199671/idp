from src import VideoConverter as VC
from src import ImagePreprocessing as im
import argparse
import os
import subprocess

if __name__ == '__main__':
    ''' Start Command Line Arguments Parser '''
    parser = argparse.ArgumentParser(description="Sensor Emulator")
    parser.add_argument('--dataset-dir', required=True, type=str,
                        help='Specify the dataset\'s root. All subdirectories containing images are found automatically'
                             'and videos are produced for each one. It is also possible to give just one directory'
                             'containing images.')
    parser.add_argument('--frame-rate', type=int, default=25,
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

    # Resolve dataset directory to find subdirectories where images (*.pngs) reside
    sub_dirs = subprocess.check_output("find {} -type f -name *.png | sed -r 's|/[^/]+$||' |sort |uniq".format(args.dataset_dir), shell=True).decode("utf-8").split("\n")[:-1]
    for i, dirs in enumerate(sub_dirs):
        if not dirs.endswith("/"):
            sub_dirs[i] = dirs + "/"

    ''' End Command Line Arguments Parser '''

    # Assign command line options to variables
    image_dirs = sub_dirs
    frame_rate = args.frame_rate
    rectify = args.rectify
    resize_factor = args.resize_factor
    upscale = args.upscale
    models_path = "./robotcar_dataset_sdk/models/"  # Path to models of sensors delivered with the oxford dataset

    # # Delete and extract the sample to get intended starting conditions.
    # # This part is just for development purposes and should be deleted later.
    # os.system("rm -r dataset")
    # os.system("mkdir dataset")
    # os.system("tar -xvf sample_small.tar -C dataset")
    # os.system("rm ./out/*.mp4")

    if rectify:
        print("Rectify images.")
        for image_dir in image_dirs:
            im.rectify_images(image_dir, models_path)

    # im.interpolate_images("sample_small/mono_left/pic00.png", "sample_small/mono_left/pic01.png")

    if resize_factor != 1:
        print("Resize images with factor {}.".format(resize_factor))
        for image_dir in image_dirs:
            im.resize_image(image_dir, factor=resize_factor)

    if upscale:
        print("Upscale images.")
        for image_dir in image_dirs:
            im.upscale_image(image_dir)

    print("Convert images to video.")
    for image_dir in image_dirs:
        VC.convert_to_video(image_dir, frame_rate=frame_rate, video_ext="mp4")
