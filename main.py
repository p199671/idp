import os

import numpy as np

from src import VideoConverter as VC
from src import ImagePreprocessing as im
import argparse
import subprocess
from src import LiDAR as LI
from scapy.utils import wrpcap

if __name__ == '__main__':
    ''' Start Command Line Arguments Parser '''
    parser = argparse.ArgumentParser(description="Sensor Emulator")
    parser.add_argument('--sensor', required=True, type=str, choices=['camera', 'lidar'],
                        help='Specify the sensor, which should be emulated.'
                             'Valid arguments are \'camera\' and \'lidar\'.')
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



    ''' End Command Line Arguments Parser '''

    # Assign command line options to variables
    sensor = args.sensor
    frame_rate = args.frame_rate
    rectify = args.rectify
    resize_factor = args.resize_factor
    upscale = args.upscale
    extension = args.extension
    data_dir = "./dataset/data/"
    models_path = "./robotcar_dataset_sdk/models/"  # Path to models of sensors delivered with the oxford dataset


    ##############################################
    ##                  Camera                  ##
    ##############################################

    # Resolve dataset directory to find subdirectories where images (*.pngs) reside
    sub_dirs = subprocess.check_output("find {} -type f -name *.png | sed -r 's|/[^/]+$||' |sort |uniq".format(data_dir), shell=True).decode("utf-8").split("\n")[:-1]
    for i, dirs in enumerate(sub_dirs):
        if not dirs.endswith("/"):
            sub_dirs[i] = dirs + "/"
    image_dirs = sub_dirs

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

        position_packet_payload = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xba\x0f\x47\x10\x20\x23\x17\x30\xf4\x0f\x56\x10\x1e\x23\xae\x3f\xc7\x0e\x6d\x10\xf1\x2f\xad\x3f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x94\xaa\xac\x17\x00\x00\x00\x00\x24\x47\x50\x52\x4d\x43\x2c\x32\x32\x30\x36\x33\x36\x2c\x41\x2c\x33\x37\x30\x37\x2e\x38\x33\x32\x33\x2c\x4e\x2c\x31\x32\x31\x33\x39\x2e\x32\x38\x36\x33\x2c\x57\x2c\x30\x30\x33\x2e\x32\x2c\x31\x34\x35\x2e\x37\x2c\x31\x31\x31\x32\x31\x32\x2c\x30\x31\x33\x2e\x38\x2c\x45\x2c\x44\x2a\x30\x44\x0d\x0a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        position_packet_counter = 1
        set_pps = False
        pps_list = []

        # Resolve dataset directory to find subdirectories where png's reside.
        lidar_dirs = subprocess.check_output(
            "find {} -type f -name *.png | sed -r 's|/[^/]+$||' |sort |uniq".format(data_dir), shell=True).decode(
            "utf-8").split("\n")[:-1]
        for i, dirs in enumerate(sub_dirs):
            if not dirs.endswith("/"):
                sub_dirs[i] = dirs + "/"

        # Find correspondent timestamps-files to directories where lidar-pngs reside.
        timestamps_dirs = []
        for dir in lidar_dirs:
            timestamps_name = str(os.path.basename(os.path.normpath(dir))) + '.timestamps'
            timestamps_path = subprocess.check_output(
                "find {} -type f -name {}".format(
                    data_dir, timestamps_name), shell=True).decode("utf-8").split("\n")[:-1]
            if timestamps_path != []:
                timestamps_dirs.append(timestamps_path[0])
            else:
                raise Exception("Timestamps file {} not found.".format(timestamps_name))

        # Iterate over found lidar directories and process the data to Velodyne HDL-32E packets.
        for i in range(len(lidar_dirs)):

            packets = []    # Variable to store all packets created out of one directory

            # Get name of directory to store pcaps later with this name
            sensor_pos = os.path.basename(lidar_dirs[i])

            # Load timestamps
            timestamps = np.loadtxt(timestamps_dirs[i], delimiter=' ', usecols=[0], dtype=np.int64)

            # Iterate over timestamps
            for l_timestamp in timestamps:
                filename = os.path.join(lidar_dirs[0], str(l_timestamp) + '.png')

                # Get raw packet content
                ranges, intensities, angles, timestamp = LI.load_velodyne_raw(filename)

                # Calculate amount of packets that can be created from the loaded data
                num_packets = timestamp.shape[1]

                # Build packets
                for i in range(num_packets):
                    # The ratio of data to position packets is 14:1, so every 15th packet is a position packet.
                    if position_packet_counter % 15 == 0:
                        position_packet = LI.build_packet(position_packet_payload, udp_s=8308, udp_d=8308)
                        packets.append(position_packet)

                    # Creation of data packet
                    pkt_ranges = ranges[:, i * 12:i * 12 + 12]
                    pkt_intensities = intensities[:, i * 12:i * 12 + 12]
                    pkt_angles = angles[:, i * 12:i * 12 + 12]
                    pkt_timestamp = timestamp[:, i]
                    payload = LI.create_velodyne_payload(pkt_ranges, pkt_intensities, pkt_angles, pkt_timestamp)
                    packet = LI.build_packet(payload)
                    position_packet_counter += 1
                    packets.append(packet)

            # Store all created packets of a directory to out/ directory.
            if not os.path.exists('out'):
                os.makedirs('out')
            out_path = 'out/{}.pcap'.format(sensor_pos)
            wrpcap(out_path, packets)
            print('Saved to {}.'.format(out_path))

        print('End.')
