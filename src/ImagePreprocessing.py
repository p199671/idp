# Imports
import os
import subprocess
from PIL import Image
import time
# from ISR.models import RDN, \
#     RRDN  # install tensorflow 1.13.1 with the command "pip install https://storage.googleapis.com/tensorflow/mac/cpu/tensorflow-1.13.1-py3-none-any.whl"
import numpy as np
from robotcar_dataset_sdk.python import image
from robotcar_dataset_sdk.python.camera_model import CameraModel


def rectify_images(image_path, model_path=None):
    """
    The function performs Bayer demosaicing and optionally undistorts the image if a model
    is given such as for the oxford dataset. The method makes use of the the function load_image
    provided in the robotcar-dataset-sdk.
    See https://robotcar-dataset.robots.ox.ac.uk/documentation/#python for more information about models.

    :param image_path: Path to the directory where the images reside, which should be rectified
    :param model_path: Path to the camera models that are contained in the robotcar_dataset_sdk
    """

    # Create the camera model to undistort the image correctly
    model = CameraModel(model_path, image_path)

    # Create a list of files of the directory
    image_list = [x for x in os.listdir(image_path) if not x.startswith('.')]

    for i, image_name in enumerate(image_list):
        im = image.load_image(image_path + image_name, model=model)
        Image.fromarray(im).save(image_path + image_name)


def interpolate_images(image_path1, image_path2):
    with Image.open(image_path1) as im1:
        with Image.open(image_path2) as im2:
            res = Image.blend(im1, im2, alpha=0.5)
            res.save("test", format="png")


def resize_image(image_path, factor=None, size=None):
    """
    The method resizes the images given in the parameter 'image_path'.
    Resizing can be done either by giving a factor, or by giving an explicit size.
    However, only one of the two parameters, 'factor' and 'size', must be specified.
    :param image_path: describes the path to the directory where the images reside
    :param factor: factor to scale images up and down
    :param size: explicit size of the form (W, H), to which the image should be resized
    """

    # Check if one of the parameters factor or size is specified.
    if not factor and not size:
        raise Exception("Either parameter 'factor' or 'size' has to be specified.")
    elif factor and size:
        raise Exception("Only one parameter, either 'factor' or 'size', must be specified.")

    # Create a list of the files of the directory
    image_list = [x for x in os.listdir(image_path) if not x.startswith('.')]

    if factor:
        for image_name in image_list:
            with Image.open(image_path + image_name) as im:
                res = im.resize((int(float(im.size[0]) * factor), int(float(im.size[1]) * factor)),
                                resample=Image.BICUBIC)
                res.save(image_path + image_name, format="png")
    elif size:
        for image_name in image_list:
            with Image.open(image_path + image_name) as im:
                res = im.resize(size)
                res.save(image_path + image_name, format="png")


def upscale_image(image_path):
    """
    This methode scales the given images up with help of the max-image-resolution-enhancer available on github
    (https://github.com/IBM/MAX-Image-Resolution-Enhancer#3-use-the-model).
    It takes the path to the directory, where the images reside, as an argument and scales each of them up as
    much as possible. The original images are replaced by the upscaled ones in the same directory.
    Make sure that the docker daemon is running for this method (systemctl start docker)!

    :param image_path: Path to the directory where the images reside.
    """

    print("Clone repository.")
    os.system("git clone https://github.com/IBM/max-image-resolution-enhancer.git")
    
    print("Modify docker image.")
    subprocess.call(
        "sed -i '19s#.*#ARG model_bucket=s3.us.cloud-object-storage.appdomain.cloud/codait-cos-max/max-image-resolution-enhancer/1.0.0#' MAX-Image-Resolution-Enhancer/Dockerfile",
        shell=True)
        
    print("Build docker image.")
    subprocess.call(
        "docker build -t max-image-resolution-enhancer max-image-resolution-enhancer/",
        shell=True)

    print("Run docker image.")
    subprocess.Popen("docker run -p 5000:5000 max-image-resolution-enhancer", shell=True,
                     stdin=None, stdout=None, stderr=None,
                     close_fds=True)  # The docker daemon must run for this command
    time.sleep(25)  # Wait till docker image is up and running.
    print("Container is running.")

    # Perform image upscaling
    image_list = [x for x in os.listdir(image_path) if not x.startswith('.')]
    for image_name in image_list:
        subprocess.call("curl -X POST \"http://localhost:5000/model/predict\" -H  \"accept: application/json\" -H  "
                        "\"Content-Type: multipart/form-data\" -F \"image=@{};type=image/png\" --output {}".format(
            image_path + image_name, image_path + image_name), shell=True)

    print("Terminate docker container.")
    subprocess.Popen("docker stop $(docker ps | grep max-image-resolution-enhancer | awk '{print $1}')",
                     shell=True)
