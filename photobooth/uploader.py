import asyncio
import os
import subprocess
from enum import Enum
from os import path
from threading import Thread

import time

import pysftp
from peewee import Model, CharField
from playhouse.sqlite_ext import SqliteExtDatabase

from photobooth import PRIVATE_KEY, REMOTE_NEW_IMAGES, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, DATABASE_PATH, REMOTE_DIR_NEW, \
    INSTAGRAM_UPLOAD


class Target(Enum):
    SERVER = 0
    INSTAGRAM = 1


class TransferStatus(Enum):
    SCHEDULED = 0
    IN_PROGRESS = 1
    COMPLETED = 2


db = SqliteExtDatabase(DATABASE_PATH)

class BaseModel(Model):
    class Meta:
        database = db


class UploadedImage(BaseModel):
    filename = CharField(unique=True)

class UploadManager(Thread):

    def __init__(self, app, upload_dir, uploaded_dir):
        super(UploadManager, self).__init__()
        self.app = app
        self.upload_dir = upload_dir
        self.uploaded_dir = uploaded_dir

        self.transfer_queue = set()
        self.transfer_status = {}
        self.canceled = False
        self.db = None
        self.setup_database()

    def setup_database(self):
        self.db = db
        self.db.connect()

        for filename in UploadedImage.select():
            self.transfer_status[filename] = TransferStatus.COMPLETED

    def abort(self):
        self.canceled = True

    def tag_files_for_upload(self):
        with self.app.transfer_lock:
            for file in os.listdir(self.upload_dir):
                filename = path.join(self.upload_dir, file)
                if path.isfile(filename) and not file == ".gitignore":
                    try:
                        UploadedImage.get(UploadedImage.filename == filename)
                    except:
                        print("{} scheduled for upload".format(filename))
                        self.transfer_queue.add(filename)
                        self.transfer_status[filename] = TransferStatus.SCHEDULED

    def upload(self, filename, target):
        try:
            with pysftp.Connection('178.62.225.50', username='root') as sftp:
                with sftp.cd(REMOTE_DIR_NEW):
                    sftp.put(filename)
        except:
            print('upload failed')


    def run(self):
        while True and not self.canceled:
            self.tag_files_for_upload()
            for filename in list(self.transfer_queue):
                try:
                    UploadedImage.create(filename=filename)
                    self.transfer_status[filename] = TransferStatus.IN_PROGRESS
                    if "main" in filename:
                        self.upload(filename, Target.INSTAGRAM)
                    else:
                        self.upload(filename, Target.SERVER)
                    self.transfer_queue.remove(filename)
                    self.transfer_status[filename] = TransferStatus.COMPLETED
                except:
                    self.transfer_status[filename] = TransferStatus.COMPLETED
                    self.transfer_queue.remove(filename)


            time.sleep(0.1)


