# Imports
import os


def rename_pics(path):
    """
    Method takes a directory as argument where the images reside and renames them according
    to the pattern "picxxxx.png".

    :param path: directory to the images
    """

    # get the files of the directory, filter out all hidden files and sort them in ascending order
    image_list = [x for x in os.listdir(path) if not x.startswith('.')]
    image_list.sort()

    digits = len(str(len(image_list)))

    # get file extension to rename files properly
    _, ext = os.path.splitext(image_list[0])

    for i, filename in enumerate(image_list):
        # renames the files according to the pattern pic%0xd.png with x as the amount of digits needed
        os.rename(path + filename, path + 'pic' + str(i).zfill(digits) + ext)


def images_to_video(path, video_ext, frame_rate):
    """
    Function takes the path to the folder with images and converts them to
    a the format specified in video_ext. The frame rate will be according to
    the given parameter 'frame_rate'

    :param path: path to the folder with the images
    :param video_ext: video extension describing the output format
    :param frame_rate: frame rate, to which the video should be converted to
    """

    # Create a list of the files of the directory
    name = os.path.basename(os.path.normpath(path))
    image_list = [x for x in os.listdir(path) if not x.startswith('.')]
    digits = len(str(len(image_list)))

    # get file extension of the images
    _, ext = os.path.splitext(image_list[0])

    # prepare the bash command
    pic_format = "{}pic%0{}d{}".format(path, digits, ext)
    vid_format = "{}.{}".format(name, video_ext)

    # create output directory if it doesn't exist yet
    if not os.path.exists('out'):
        os.makedirs('out')

    # bash command to start the video convertion with ffmpeg
    os.system("ffmpeg -r {} -i {} out/{}".format(frame_rate, pic_format, vid_format))


def convert_to_video(path, video_ext="mp4", frame_rate=25):
    """
    This method combines the two previous methods in order to generate a video file.

    :param path: path to the images
    :param video_ext: output format of the video (e.g. mp4, mov, wmv, flv, avi, webm, mkv, ...)
    :param frame_rate: frame rate of the video
    """
    rename_pics(path)
    images_to_video(path, video_ext, frame_rate)
