import os

class Config(object):
    def __init__(self):
        self.mpd.port=6600
        self.mpd.host="localhost"
        self.server.port=80
        self.server.tagformat="<b>%(artist)s</b> - %(title)s"

if __name__ == "__main__":
    pass
