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



import base64
u64enc = base64.urlsafe_b64encode
u64dec = base64.urlsafe_b64decode

class PlayLists(wPlugin):

    def show(self):
        return """
            <button onclick='ajax_listePL()'>Playlists</button>
        """

    def ajax_listePL(self):
        yield "<h2>Playlists</h2>"
        l=self.mpd.getPlaylistNames()
        for i in l:
            classe = l.index(i)%2==0 and " class='p'" or ''
            yield "<li%s>"%classe
            yield """<a href='#' onclick='ajax_playPL("%s");'><span>></span></a>""" % (u64enc(i.path),)
            yield i.path
            yield "</li>"

    def ajax_playPL(self,pl_enc):
        pl=u64dec(pl_enc)
        self.mpd.load(pl)

        return "player" # tell to update player
