from PIL import Image, ImageFilter, ImageEnhance
from shutil import copyfile
import colorsys

def load_image(image_path):
    try:
        image = Image.open(image_path)
        return image
    except Exception as e:
        print('Unable to load image')

def dupe_image(image_path, options):
    if options == 'copy':
        copyfile(image_path, image_path + '.copy')
    elif options == 'replace':
        copyfile(image_path + '.copy', image_path)

def get_default_slider():
    return {'color': 1, 'bright': 1, 'contrast': 1, 'sharp': 1}

def get_image_size(image):
    return image.width, image.height

# ROTATE
def rotate_image(image_path, angle):
    image = load_image(image_path)
    image = image.rotate(angle)
    image.save(image_path)

# RESIZE
def resize_image(image_path, width, height):
    image = load_image(image_path)
    image = image.resize((width, height), Image.BICUBIC)
    image.save(image_path)

# CROP
def crop_image(image_path, start_x, start_y, end_x, end_y):
    image = load_image(image_path)
    image = image.crop((start_x, start_y, end_x, end_y))
    image.save(image_path)
