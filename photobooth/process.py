import os
import shutil
from os.path import isfile, join
from threading import Thread
from uuid import uuid4

import PIL.Image

from photobooth import WATERMARK
from photobooth.render import create_collage


class ThreadedMover(Thread):
    def __init__(self, processor, batch_code):
        super(ThreadedMover, self).__init__()
        self.processor = processor
        self.batch_code = batch_code

    def run(self):
        for file in os.listdir(self.processor.in_dir):
            filename = join(self.processor.in_dir, file)
            if isfile(filename) and self.batch_code in file:
                self.processor.watermark(filename)
                with self.processor.app.transfer_lock:
                    shutil.move(filename, join(self.processor.out_dir, self.processor.get_filename()))


class ImageProcessor(object):
    def __init__(self, app, options, in_dir, out_dir):
        self.app = app
        self.options = options
        self.in_dir = in_dir
        self.out_dir = out_dir

    def on_collage_complete(self, image):
        filename = self.get_filename()
        file_location = join(self.out_dir, 'main-{}'.format(filename))
        image.save(file_location)
        self.watermark(file_location)
        t = ThreadedMover(self, self.app.camera.get_batch_code())
        t.start()

        self.app.next_image(file_location)

    def process(self):
        self.app.clear_next()
        from photobooth.app import PhotobootStatus
        self.app.status = PhotobootStatus.PROCESSING
        files = []
        for file in os.listdir(self.in_dir):
            if isfile(join(self.in_dir, file)) and not file == ".gitignore":
                files.append(join(self.in_dir, file))

        # Single shot
        if len(files) == 1:
            filename = self.get_filename()
            with self.app.transfer_lock:
                file_location = join(self.out_dir, 'main-{}'.format(filename))
                shutil.move(files[0], file_location)
            self.watermark(file_location)
            self.app.next_image(file_location)
        elif len(files) > 1:
            # Create a collage.
            create_collage(files, self.options, self.on_collage_complete)

    def get_filename(self):
        return "{}.jpg".format(str(uuid4()))

    def watermark(self, filename):
        """ Apply a watermark to an image """
        mark = PIL.Image.open(WATERMARK)
        im = PIL.Image.open(filename)
        im.resize((3888, 2592), PIL.Image.ANTIALIAS)
        if im.mode != 'RGBA':
            im = im.convert('RGBA')
        layer = PIL.Image.new('RGBA', im.size, (0, 0, 0, 0))
        position = (im.size[0] - mark.size[0], im.size[1] - mark.size[1])
        layer.paste(mark, position)
        PIL.Image.composite(layer, im, layer).save(filename)
