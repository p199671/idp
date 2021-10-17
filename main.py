import os

import numpy as np

from src import VideoConverter as VC
from src import ImagePreprocessing as im
import argparse
import subprocess
from src import LiDAR as LI
from scapy.layers.inet import Ether, IP, UDP
from scapy.utils import wrpcap

if __name__ == '__main__':
    ''' Start Command Line Arguments Parser '''
    parser = argparse.ArgumentParser(description="Sensor Emulator")
    parser.add_argument('--sensor', required=True, type=str, choices=['camera', 'lidar'],
                        help='Specify the sensor, which should be emulated.'
                             'Valid arguments are \'camera\' and \'lidar\'.')
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
    parser.add_argument('--extension', type=str, default='mp4',
                        help='This option defines the extension of the video produced out of the'
                             'camera raw data. Valid extensions are mp4, avi and all supported by ffmpeg.')

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
    sensor = args.sensor
    image_dirs = sub_dirs
    frame_rate = args.frame_rate
    rectify = args.rectify
    resize_factor = args.resize_factor
    upscale = args.upscale
    extension = args.extension
    models_path = "./robotcar_dataset_sdk/models/"  # Path to models of sensors delivered with the oxford dataset


    ##############################################
    ##                  Camera                  ##
    ##############################################

    if sensor == 'camera':

        if rectify:
            print("Rectify images.")
            for image_dir in image_dirs:
                im.rectify_images(image_dir, models_path)

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
            VC.convert_to_video(image_dir, frame_rate=frame_rate, video_ext=extension)



    ##############################################
    ##                  LiDAR                   ##
    ##############################################

    if sensor == 'lidar':
        packets = []

        # Get and adjust the director of lidar pngs
        velodyne_dir = args.dataset_dir
        if velodyne_dir[-1] == '/':
            velodyne_dir = velodyne_dir[:-1]

        # Check that the directory structure is right
        velodyne_sensor = os.path.basename(velodyne_dir)
        if velodyne_sensor not in ["velodyne_left", "velodyne_right"]:
            raise ValueError("Velodyne directory not valid: {}".format(velodyne_dir))

        # Get path to timestamps file
        timestamps_path = velodyne_dir + '.timestamps'
        if not os.path.isfile(timestamps_path):
            raise IOError("Could not find timestamps file: {}".format(timestamps_path))

        # Load timestamps
        velodyne_timestamps = np.loadtxt(timestamps_path, delimiter=' ', usecols=[0], dtype=np.int64)

        # Iterate over timestamps
        for velodyne_timestamp in velodyne_timestamps:
            filename = os.path.join(velodyne_dir, str(velodyne_timestamp) + '.png')

            # Get raw packet content
            ranges, intensities, angles, timestamp = LI.load_velodyne_raw(filename)

            # Calculate amount of packets that can be created from the loaded data
            num_packets = timestamp.shape[1]
            for i in range(num_packets):
                pkt_ranges = ranges[:, i*12:i*12+12]
                pkt_intensities = intensities[:, i*12:i*12+12]
                pkt_angles = angles[:, i*12:i*12+12]
                pkt_timestamp = timestamp[:, i]
                payload = LI.create_velodyne_payload(pkt_ranges, pkt_intensities, pkt_angles, pkt_timestamp)
                packet = Ether()/IP()/UDP(dport=65535, sport=0)/payload
                packets.append(packet)

        if not os.path.exists('out'):
            os.makedirs('out')
        out_path = 'out/{}.pcap'.format(velodyne_sensor)
        wrpcap(out_path, packets)

        print('End.')
