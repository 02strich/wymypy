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
from flask import make_response
from string import Template

import config
from plugins import wPlugin

class CiscoRadio(wPlugin):
    def init(self):
        pass
    
    def index(self):
        resp = make_response(Template("""<CiscoIPPhoneMenu>
<Title>WyMyPy</Title>
<Prompt>Play Music NOW !</Prompt>
<MenuItem>
    <Name>Play - Pause</Name>
    <URL>http://$server/plugin/cisco/playpause</URL>
</MenuItem>
<MenuItem>
    <Name>Stop</Name>
    <URL>http://$server/plugin/cisco/stop</URL>
</MenuItem>
<MenuItem>
    <Name>Volume Up</Name>
    <URL>http://$server/plugin/cisco/volup</URL>
</MenuItem>
<MenuItem>
    <Name>Volume Down</Name>
    <URL>http://$server/plugin/cisco/voldown</URL>
</MenuItem>
<MenuItem>
    <Name>Next</Name>
    <URL>http://$server/plugin/cisco/next</URL>
</MenuItem>
<MenuItem>
    <Name>Previous</Name>
    <URL>http://$server/plugin/cisco/prev</URL>
</MenuItem>
</CiscoIPPhoneMenu>""").substitute(server=config.SERVER_NAME), 200)
        resp.headers['Content-type'] = 'text/xml'
        resp.headers['Connection'] = 'close'
        resp.headers['Expires'] = '-1'
        return resp
    
    def playpause(self):
        self.mpd.pause()
        return self.index()
    
    def stop(self):
        self.mpd.stop()
        return self.index()
    
    def next(self):
        self.mpd.next()
        return self.index()
    
    def prev(self):
        self.mpd.prev()
        return self.index()
    
    def volup(self):
        self.mpd.volumeUp()
        return self.index()
    
    def voldown(self):
        self.mpd.volumeDown()
        return self.index()