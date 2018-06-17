import os
import re
import shutil
import subprocess
import time


class Camera(object):
    def __init__(self, app, model_name, output_directory):
        data = subprocess.check_output('gphoto2 --auto-detect', shell=True)
        print(data)
        camera_detected = model_name in data

        assert camera_detected, "No camera found with model name {}".format(model_name)
        assert os.path.isdir(output_directory), "{} not a directory or does not exist".format(output_directory)

        self.app = app
        self.model_name = model_name
        self.output_directory = output_directory
        self.batch = 0

    def take_picture(self, count=1, interval=1):
        self.batch += 1
        try:
            assert interval >= 1, "Interval can't be less than 1"
            assert count > 0, "Count has to be highter than one"
            picture_count = count

            while picture_count != 0:

                result = subprocess.check_output('gphoto2 --trigger-capture --keep', shell=True)
                time.sleep(interval)
                if self._check_picture_result(result):
                    picture_count -= 1
                else:
                    print("Camera busy")

            print("Succesfully took {} pictures".format(count))
            subprocess.call('gphoto2 --list-files', shell=True)
        except subprocess.CalledProcessError:
            self.app.reset()

    def download_images(self):
        try:
            batch_code = self.get_batch_code()
            output = subprocess.check_output('gphoto2 --get-all-files', shell=True)
            files = re.findall('IMG_\d+.JPG', str(output))

            for file in files:
                shutil.move(file, os.path.join(self.output_directory, '{}-{}'.format(batch_code, file)))

            subprocess.call('gphoto2 --delete-all-files --recurse', shell=True)
        except subprocess.CalledProcessError:
            self.app.reset()

    def get_batch_code(self):
        return 'B{0:04d}'.format(self.batch)

    @classmethod
    def _check_picture_result(cls, result):
        busy = b'PTP Device Busy' in result
        return not busy
