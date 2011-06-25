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

import os
from wymypy.plugins import wPlugin

class Library(wPlugin):
    
    def init(self):
        self.button_index = 1
    
    def show(self):
        return """
            <button onclick='ajax_library("")'>Library</button>
        """
    
    def ajax_library(self, dir):
        go_library = lambda link, aff: """<a href="#" onclick='ajax_library("%s")'>%s</a>""" % (link, aff)
        go_add = lambda f: """<a href='#' onclick='ajax_ladd("%s");'>%s</a>""" % (f, "<span>&gt;</span>")
        if dir != "":
            yield "<h2>"
            path = ""
            yield go_library("", "Library")
            for i in dir.split("/"):
                yield " / "
                if path != "":
                    path += "/"
                path += i
                if path != dir:
                    yield go_library(path, i)
                else:
                    yield i
            yield go_add(dir)
            yield "</h2>"
        else:
            yield "<h2>Library</h2>"
        
        l = self.mpd.ls([dir], onlyDirs=True)
        l.sort(cmp=lambda a, b: cmp(a.lower(), b.lower()))
        c = 0
        for s in l:
            classe = (c % 2 == 0) and " class='p'" or ''
            yield "<li%s>" % classe
            yield go_library(s, os.path.basename(s))
            yield "</li>"
            c += 1
        
        l = self.mpd.ls([dir], onlyFiles=True)
        l.sort(cmp=lambda a, b: cmp(a.lower(), b.lower()))
        for s in l:
            classe = (c % 2 == 0) and " class='p'" or ''
            yield "<li%s>" % classe
            yield go_add(s)
            yield self.go_listen(s)
            yield os.path.basename(s)
            yield "</li>"
            c += 1
    
    def ajax_ladd(self, f):
        self.mpd.add([f, ])
        return "player"  # tell to update player
