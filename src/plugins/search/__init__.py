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
import base64
u64enc = base64.urlsafe_b64encode
u64dec = base64.urlsafe_b64decode

class Search(wPlugin):

    def show(self):
        return """
            <form onsubmit='ajax_search($("tq").value,$("q").value);return false'>
            <input type='text' id='q' size="10"/>
            <select id='tq'>
                <option value='filename'>filename</option>
                <option value='artist'>artist</option>
                <option value='album'>album</option>
                <option value='title'>title</option>
            </select>
            <button type='submit'>search</button>
            </form>
        """

    def ajax_search(self,tq,q):
        q=q.strip()
        yield "<h2>Search for '"
        yield q
        yield "' in "
        yield tq
        yield "</h2>"
        if len(q)>1:
            l=self.mpd.search(tq, q)
            for i in l:
                p = os.path.dirname(i)
                f = os.path.basename(i)
                classe = l.index(i)%2==0 and " class='p'" or ''
                yield "<li%s>"%classe
                yield """<a href='#' onclick='ajax_add("%s");'>%s</a>"""%(u64enc(i),"<span>></span>")
                yield self.go_listen(i)
                yield f
                #~ yield "<br />"
                #~ yield go_library(p,p)
                yield "</li>"

    def ajax_add(self,f_enc):
        f=u64dec(f_enc)
        self.mpd.add([f,])

        return "player" # tell to update player

