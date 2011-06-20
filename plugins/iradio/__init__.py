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
from couchdbkit import *

import config

class Greeting(Document):
    url = StringProperty()


class IRadio(wPlugin):
    def init(self):
        self.button_index = 50
        self.server = Server(uri=config.COUCHDB_URL)
        self.db = self.server.get_or_create_db("mpd_radio")
    
    def show(self):
        return """
            <button onclick='ajax_radio()'>Radio</button>
        """
    
    def ajax_radio(self, ignore=0):
        yield "<h2>Internet Radio</h2>"
        
        # list stations
        index = 0
        for i in self.db.all_docs().all():
            cur = self.db.get(i['id'])
            classe = index % 2 == 0 and " class='p'" or ''
            yield "<li%s>" % classe
            yield """<a href='#' onclick='ajax_streamPlay("%s");'><span>></span></a>""" % (cur['url'])
            yield cur['url']
            yield "</li>"
            index += 1
        
        # add new station
        yield "<h3>Add Internet Station:"
        yield """
          <form onsubmit='ajax_streamAdd($("radio").value);return false'>
            <input type='text' id='radio' size="10"/>
            <button type='submit'>add</button>
          </form>
        """
    
    def ajax_streamPlay(self, url):
        self.mpd.add([url])
        return "player"
    
    def ajax_streamAdd(self, f):
        self.db.save_doc({'url': f})
        for ele in self.ajax_radio():
            yield ele
        #return "player"
