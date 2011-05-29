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
try:
    import sys
    sys.path.append("../..")
    from plugins import wPlugin
except:
    pass


import os


class LastFM(wPlugin):

    def show(self):
        return """
            <button onclick='ajax_lastfm("")'>LastFM</button>
        """

    def ajax_lastfm(self, t, rsrnd=0):
	yield "<h2>Last.fm</h2>"
	# embedded LastFMProxy
	yield """
	  <div align="center">
	  <iframe src="http://media:1881" width="95%" height="215px" frameborder="0">
	  <p>Ihr Browser kann leider keine eingebetteten Frames anzeigen.</p>
	  </iframe>
	  </div>
	"""
	
	# added LastFM station
	yield "<h3>Add Last.fm Station:"
	yield """
	  <form onsubmit='ajax_fmadd($("station").value);return false'>
	    <input type='text' id='station' size="10"/>
	    <button type='submit'>add</button>
          </form>
	"""

	# added LastFM station
	yield "<h3>Add Internet Station:"
	yield """
	  <form onsubmit='ajax_streamadd($("radio").value);return false'>
	    <input type='text' id='radio' size="10"/>
	    <button type='submit'>add</button>
          </form>
	"""



    def ajax_fmadd(self, f, rsrnd=0):
       	if f.startswith("http://www.lastfm.de/listen/"):
		f=f.replace("http://www.lastfm.de/listen/", "")
	if f.startswith("http://www.lastfm.de/"):
		f=f.replace("http://www.lastfm.de/", "")
	url="http://media:1881/"+f+".mp3"
       	self.mpd.add([url])

        return "player" # tell to update player

    def ajax_streamadd(self, f, rsrnd=0):
    	self.mpd.add([f])
	return "player"

