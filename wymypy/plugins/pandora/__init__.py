#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#      wymypy.py
#
#      Copyright 2007 Marc Lentz <manatlan@gmail.com>
#
#      This program is free software; you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation; either version 2 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program; if not, write to the Free Software
#      Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
import time
import threading
import urllib2
from pandora import Pandora as PandoraPython

import wymypy.config
from wymypy.plugins import wPlugin

class WorkerThread(threading.Thread):
    def __init__(self, MPD, pandora):
        threading.Thread.__init__(self)
        self.mpd     = MPD
        self.pandora = pandora
        self.playing = False
    
    def run(self):
        while True:
            if self.playing:
                idx, tot = self.mpd.getPlaylistPosition()
                if wymypy.config.DEBUG: print "Current space left: " + str(tot - idx)
                if tot - idx < 3:
                    for i in range(0,2):
                        song = self.pandora.getNextSong()
                        self.mpd.add([song['audioURL']])
            time.sleep(5)

class Pandora(wPlugin):
    def init(self):
        self.button_index = 51
        
        # setup proxy
        if wymypy.config.PANDORA_PROXY:
           proxy_support = urllib2.ProxyHandler({"http" : wymypy.config.PANDORA_PROXY})
           opener = urllib2.build_opener(proxy_support)
           urllib2.install_opener(opener)
        
        # setup pandora
        self.pandora = PandoraPython()
        if not self.pandora.authenticate(username=wymypy.config.PANDORA_USERNAME, password=wymypy.config.PANDORA_PASSWORD):
            raise ValueError("Wrong pandora credentials or proxy supplied")
        self.stationCache = self.pandora.getStationList()
        
        self.currentStationId = None
        self.currentStationName = None
        self.playing = False
        
        self.worker = WorkerThread(self.mpd, self.pandora)
        self.worker.daemon = True
        self.worker.start()
    
    def show(self):
        return """
            <button onclick='ajax_pandora()'>Pandora</button>
        """
    
    def ajax_pandora(self):
        yield "<h2>Pandora Radio</h2>"
        
        # current station + options
        yield "Current station: " + str(self.currentStationName)
        if self.playing:
            yield """ <button onclick='ajax_pandoraOpe("stop");'>[]</button>"""
        else:
            yield """ <button onclick='ajax_pandoraOpe("play");'>></button>"""
        
        # list stations
        index = 0
        for station in self.stationCache:
            classe = index % 2 == 0 and " class='p'" or ''
            yield "<li%s>" % classe
            yield """<a href='#' onclick='ajax_switchStation("%s", "%s");'><span>></span></a>""" % (station['stationId'], station['stationName'].replace("'", ""))
            yield station ['stationName']
            yield "</li>"
            index += 1
    
    def ajax_switchStation(self, stationdId, stationName):
        self.currentStationId = stationdId
        self.currentStationName = stationName
        self.pandora.switchStation(stationdId)
        
        return self.ajax_pandora()
    
    def ajax_pandoraOpe(self, op):
        if op == "play" and self.currentStationId:
            self.playing = True
            self.worker.playing = True
        else:
            self.playing = False
            self.worker.playing = False
        return self.ajax_pandora()
    
