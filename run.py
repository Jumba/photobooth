import os

import sys

from photobooth.app import PhotoboothApplication


if __name__ == '__main__':
    app = PhotoboothApplication(sys.argv)
    app.setup_photobooth(b'Canon')
    print("app starting")
    sys.exit(app.exec_())


