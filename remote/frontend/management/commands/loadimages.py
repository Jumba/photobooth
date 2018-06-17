from django.core.management.base import BaseCommand, CommandError
from remote.frontend.models import Photo
from django.conf import settings
from PIL import Image


from os import listdir
from os.path import isfile, join


class Command(BaseCommand):
    help = 'Processes uploaded images'


    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        files = [f for f in listdir(settings.PATH_RAW) if isfile(join(settings.PATH_RAW, f))]
        for file in files:
            photo = Photo.objects.filter(filename=file).first()
            if not photo:
                self.stdout.write("Processing {}".format(file))
                out = self.scale_image(file)
                self.stdout.write("Processing {} completed: {}".format(file, out))



    def scale_image(self, filename):
        raw_path = join(settings.PATH_RAW, filename)
        scaled_path = join(settings.PATH_SCALED, filename)
        thumb_path = join(settings.PATH_THUMBS, filename)

        # First pass for the scaled version
        try:
            image = Image.open(raw_path)
            image.thumbnail(settings.SCALED_SIZE)
            image.save(scaled_path, "JPEG")
        except:
            return False

        # Second pass for the thumb version
        try:
            image = Image.open(raw_path)
            image.thumbnail(settings.THUMBNAIL_SIZE)
            image.save(thumb_path, "JPEG")
        except:
            return False

        photo = Photo()
        photo.filename = filename
        photo.path_raw = raw_path
        photo.path_scaled = scaled_path
        photo.path_thumb = thumb_path

        photo.save()
        return True



