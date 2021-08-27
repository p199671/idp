import os


def start_gstreamer_server(video_path, dst_address, dst_port=9001):
    """
    The method starts a server with the help of gstreamer which creates a stream of the provided video in video_path.
    :param video_path: provides the path to the video that should be streamed
    :param dst_address: provides the ipv4 address to which the video stream is addressed
    :param dst_port: destination port is set to 9001 if not defined differently
    """
    os.system("gst-launch-1.0 -v filesrc location = " + video_path + "! decodebin ! x264enc ! rtph264pay ! udpsink "
                                                                     "host=" + dst_address + " port=9001")

def start_gstreamer_client():
    os.system("gst-launch-1.0 -v udpsrc port=9001 caps = \"application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96\" ! rtph264depay ! decodebin ! videoconvert ! autovideosink")