# Where to spit out our qrcode, watermarked image, and local html
import os
from os.path import expanduser, join

current_directory = os.getcwd()

NEW_IMAGES = join(current_directory, 'out', 'new_images')
PROCESSED_IMAGES = join(current_directory, 'out', 'processed_images')
UPLOADED_IMAGES = join(current_directory, 'out', 'uploaded_images')
DATABASE_PATH = join(current_directory, 'database.db')

# The watermark to apply to all images
WATERMARK = join(current_directory, 'resources', 'brua-ron.png')

REMOTE_DIR_NEW = '/var/www/raw'

REMOTE_NEW_IMAGES = 'root@178.62.225.50:/var/www/raw'
PRIVATE_KEY = expanduser('~/.ssh/id_rsa')

HTTP_SERVE_URL = 'http://arosbrua.nl:8000/raw/'

# Size of the qrcode pixels
QR_CODE_SIZE = 10

QUALITY_SKEL = 0
QUALITY_FAST = 1
QUALITY_BEST = 2

INSTAGRAM_UPLOAD = True
INSTAGRAM_USERNAME = 'arosbrua'
INSTAGRAM_PASSWORD = ''

class Options(object):
    def __init__(self):
        self.border_w = 0.01
        self.border_c = "black"
        self.out_w = 5184
        self.out_h = 3456
        self.multi_col = False
