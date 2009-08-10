#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import dict4ini

class Config(dict4ini.DictIni):
    file = ".wymypy"

    def __init__(self):
        file = os.path.join( os.path.expanduser("~"), Config.file )
        dict4ini.DictIni.__init__(self,file)
        if not os.path.isfile(file):
            self.makeDefault()

    def makeDefault(self):
        print "Create config file, in home :",Config.file
        self.mpd.port=6600
        self.mpd.host="localhost"
        #self.server.port=8080
        self.server.port=80
        self.server.tagformat="<b>%(artist)s</b> - %(title)s"
        self.save()


if __name__ == "__main__":
    pass
