import os
import cv2
import numpy as np
from scapy.layers.inet import Ether, IP, UDP

# Flag for Velodyne HDL-32E packets as specified
# in the manual (https://gpsolution.oss-cn-beijing.aliyuncs.com/manual/LiDAR/MANUAL%2CUSERS%2CHDL32E.pdf)
flag = b'\xff\xee'
factory_byte = b'\37\21'


def load_velodyne_raw(velodyne_raw_path):
    """Decode a raw Velodyne example. (of the form '<timestamp>.png')
    Args:
        example_path (AnyStr): Oxford Radar RobotCar Dataset raw Velodyne example path
    Returns:
        ranges (np.ndarray): Range of each measurement in meters where 0 == invalid, (32 x N)
        intensities (np.ndarray): Intensity of each measurement where 0 == invalid, (32 x N)
        angles (np.ndarray): Angle of each measurement (azimuth) (1 x N)
        approximate_timestamps (np.ndarray): Timestamps of each mesaurement (1 x N). Only every 12th timestamp
                                            is needed since the other are interpolated and do not correspond
                                            to packets.

    """
    ext = os.path.splitext(velodyne_raw_path)[1]
    if ext != ".png":
        raise RuntimeError("Velodyne raw file should have `.png` extension but had: {}".format(ext))
    if not os.path.isfile(velodyne_raw_path):
        raise FileNotFoundError("Could not find velodyne raw example: {}".format(velodyne_raw_path))

    example = cv2.imread(velodyne_raw_path, cv2.IMREAD_GRAYSCALE)
    intensities, ranges_raw, angles_raw, timestamps_raw = np.array_split(example, [32, 96, 98], 0)
    ranges = np.ascontiguousarray(ranges_raw.transpose()).view(np.uint16).transpose()  # distance

    angles = np.ascontiguousarray(angles_raw.transpose()).view(np.uint16).transpose()  # azimuth

    approximate_timestamps = np.ascontiguousarray(timestamps_raw.transpose()).view(np.int64).transpose()
    timestamps = approximate_timestamps[:, ::12]
    return ranges, intensities, angles, timestamps


def create_velodyne_payload(ranges, intensities, angles, timestamp):
    '''
    This function creates the payload for exactly one packet with HDL-32E Single Return mode data structure
    (as shown in Figure 9-2 of the manual https://gpsolution.oss-cn-beijing.aliyuncs.com/manual/LiDAR/MANUAL%2CUSERS%2CHDL32E.pdf).
    :param ranges: Range of each measurement in meters where 0 == invalid, (32 x N)
    :param intensities: Intensity of each measurement where 0 == invalid, (32 x N)
    :param angles: Angle of each measurement (azimuth) (1 x N)
    :param timestamp: Real timestamps of each mesaurement (1 x N).
    :return: Payload for one velodyne hdl-32e packet.
    '''
    payload = b''

    for i in range(12):
        payload += flag  # Add flag
        payload += dec_to_hexbyte(angles[0, i], num_bytes=2)
        for j in range(32):
            payload += dec_to_hexbyte(ranges[j, i], num_bytes=2)
            payload += dec_to_hexbyte(intensities[j, i])

    payload += dec_to_hexbyte(convert_timestamp(timestamp[0]), num_bytes=4)
    payload += factory_byte
    return payload


def dec_to_hexbyte(dec, num_bytes=1):
    hex = format(dec, 'x')
    while len(hex) < num_bytes * 2:
        hex = '0' + hex

    hexbyte = bytes.fromhex(hex)
    return hexbyte


def convert_timestamp(timestamp):
    '''
    This function converts a given unix timestamp in microseconds to a 32 bit timestamp,
    referring to the last top of the hour. This format is needed to properly build
    velodyne packets.
    :param timestamp: Unix (64 bit) timestamp in microseconds
    :return: Elapsed time in microseconds since the top of the hour / timestamp for velodyne packet
    '''
    velodyne_timestamp = timestamp % 3600000000
    return velodyne_timestamp


def build_packet(payload, eth_s="60:76:88:20:12:6e", eth_d="ff:ff:ff:ff:ff:ff", ip_s="192.168.1.201", ip_d="255.255.255.255", udp_s=2368, udp_d=2368):
    '''
    Builds a packet based on input variables.
    :param payload: Is either data or position packet payload.
    :param ip_s: Source IP address
    :param ip_d: Destination IP address
    :param udp_s: Source UDP port
    :param udp_d: Destination UDP port
    :return: The whole assembled packet.
    '''
    packet = Ether(src=eth_s, dst=eth_d)/IP(src=ip_s, dst=ip_d)/UDP(sport=udp_s, dport=udp_d)/payload
    return packet
