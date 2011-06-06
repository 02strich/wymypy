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
# #############################################################################
# Configuration
# #############################################################################

# #############################################################################
import os
import time
import sys
import cgi
import socket
from urllib import urlencode

import config
from libs.mpdsafe import MpdSafe
from libs import wsgiserver
from libs.utilities import get_post_form,explodePath
import base64
u64enc = base64.urlsafe_b64encode
u64dec = base64.urlsafe_b64decode

MPD = None

__version__="1.3"

try:
    os.chdir(os.path.dirname(__file__))
except:
    pass

from plugins import wPlugin # import in __builtins__ !!!


def register_ajax(path,method):
    return """
    function ajax_%(method)s()
    { sajax_do_call("%(path)s%(method)s",ajax_%(method)s.arguments);}
    """ % locals()


class WyMyPy:
    def __init__(self, plugins_dict):
        self.plugins = plugins_dict
    
    def __call__(self,environ, start_response):
        path = environ["PATH_INFO"]
        
        f,mpath = explodePath(path)
        if f == "":
            if mpath == "/dewplayer.swf":
                start_response('200 OK', [('content-type', 'application/x-shockwave-flash')])
                return open("libs/dewplayer.swf","rb")
            else:
                start_response('200 OK', [('content-type', 'text/html')])
                return self.mainpage()
        elif f == "__ajax":
            start_response('200 OK', [('content-type', 'text/html')])
            args = [i.value for i in get_post_form(environ).list]
            return self.makeajax(mpath, args)
        elif f == "listen":   # plugin shouldn't named "listen" !
            name = u64dec(mpath[1:])
            start_response('200 OK', [('content-type', 'application/octet-stream'),
                    ("Content-Disposition","""attachment; filename="%s";"""%name)
                ])
            #file=os.path.join("/media/data/mp3",name)
            file=os.path.join("/var/lib/mpd/music",name)
            return open(file,"rb")
        else: # it should be a plugin now !
            i = self.plugins[f.lower()]
            if i:
                # it's a plugin "get"
                # TODO : sometimes content-type should be image
                start_response('200 OK', [('content-type', 'text/html')])
                return i.get(mpath)
            else:
                start_response('404 not found', [('content-type', 'text/html')])
                return ("404 not found",)
    
    def mainpage(self):
        yield """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
                    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en-US" />
                    <html>
                      <head>
                        <meta http-equiv="content-type" content="text/html; charset=utf-8" />
                        <meta http-equiv="content-language" content="en-US" />
                        <meta name="language" content="en-US" />
                        <meta name="description" content="Official website of the web-band manella">
                        <title>wymypy</title>
              """
        #======================================================
        # CSS
        #======================================================
        yield "<style type='text/css'>"
        
        # main page css
        input_file = open("templates/main.css", "r")
        yield input_file.read()
        input_file.close()
        
        # plugin css
        for i in self.plugins.values():
            yield i.css
        
        yield "</style>"
        
        #======================================================
        # AJAX JavaScript
        #======================================================
        yield "<script type='text/javascript'>"
        am = AjaxMethods()
        for i in dir(am):
            if str(i).lower().startswith("ajax_"):
                yield register_ajax("/__ajax/", i[5:])
        
        
        for plugin in self.plugins.values():
            for i in dir(plugin):
                if str(i).lower().startswith("ajax_"):
                    yield register_ajax("/__ajax/" + plugin.path + "/", i[5:])
        
        #=======================================================
        # normal JavaScript
        #=======================================================
        # main page js
        input_file = open("templates/main.js", "r")
        yield input_file.read()
        input_file.close()
        
        # plugin js
        for i in self.plugins.values():
            yield i.js
        yield "</script>"
        
        #=======================================================
        # HTML
        #=======================================================
        yield """ </head>
                  <body onload="init();">
              """
        
        yield """<div id="zonePlugins">"""
        for i in sorted(self.plugins.values(), key = lambda plugin: plugin.button_index):
            yield i.show()
        yield """</div>"""
        
        yield """<div id="zoneOpt">
                   <b style='float:right'><a href='http://manatlan.infogami.com/wymypy'>wymypy</a> %s</b>
                   <select id='timer' onchange="refresh();">
                     <option value='1000'>refresh 1s</option>
                     <option value='2000'>refresh 2s</option>
                     <option value='5000' selected>refresh 5s</option>
                     <option value='10000'>refresh 10s</option>
                     <option value=''>refresh none</option>
                   </select>
                   <input type="checkbox" id='dispTags' onchange='changeDisplay(this);' />
              </div>""" % __version__
        yield """<div id="zoneListen"></div>"""
        yield """<div id="zonePlayer"></div>"""
        yield """<div id="zoneView">
        <h1>Welcome</h1>
        Welcome to wymypy ! From here you can pilot your Music Player Daemon!
        <br><br>
        <p>At the top, you have the "plugin bar" with provide the main operations in your library. Plugins will always be displayed in this zone.</p>
        <p>At the right, you can control your player, and your playlist.</p>
        <p>At the bottom right, you find the wymypy options now.</p>
        <p>Other configurations take place in your <b>~/.wymypy</b> config file (in the future they will be editable thru a plugin)</p>
        </div>"""
        yield """<div id="zonePlayList"></div>"""
        
        yield """  </body>
                </html>
                """ % locals()
    
    def makeajax(self, method, args):
        pmethod = method

        # corrects args (undefined -> None)
        largs = []
        for i in args:
          if i=="undefined":
            largs.append(None)
          else:
            largs.append(i)
        args=largs

        if method.count("/")==2:
            # plugin ("/Plugin/method")
            t=method.split("/")
            inst = self.plugins[t[1].lower()]
            method = t[2]
            isPlugin=True
        else:
            inst = AjaxMethods()
            method = method[1:] # strip the first /
            isPlugin=False

        # la methode autoinstancié se nomme "ajax_*"
        method = "ajax_"+method
        if hasattr(inst,method):
            fct=getattr(inst,method)
            iter=fct(*(args),**({}))
            if isPlugin:
                if "'generator'" in str(type(iter)):
                    def _iterInZoneView(iter):
                        yield "[[zoneView]]"
                        for i in iter:
                            yield i
                    iter = _iterInZoneView(iter)
                else:
                    if iter=="player":  #plugin ajax method returns "player" -> redraw player
                        inst = AjaxMethods()
                        iter = inst.ajax_player()
                    else:
                        yield """+ {"":""}"""
                        return

            dic=flux2dict( iter )
            #~ print "AJAXCALL:",pmethod,args,"--->",dic.keys()
            yield "+ "
            yield jsonize(dic)
        else:
            yield "- methode non existante : ",pmethod

def flux2dict( iter ):
    l={}
    key=None
    for i in iter:
      if i[:2]=="[[" and i[-2:]=="]]":
        key=i[2:-2]
        l[key]=""
      else:
        if key==None:
          raise "key error"
        else:
          l[key]+=i
    return l

def jsonize(dict):
    return "{"+",".join([""" "%s" : "%s" """ % (i,dict[i].replace('"','\\"').replace('\n','\\n')) for i in dict])+"}"



def getUrlsForMpdSong(s):
    if s.path.lower().startswith("http://"):
        # radio
        if "-" in s.title:
            l = s.title.split("-")
            artist = l[0].strip()
            title  = l[1].strip()
            album  = ""
        else:
            return  {}
    else:
        artist = s.artist.strip()
        title  = s.title.strip()
        album  = s.album.strip()
    
    url = {}
    if artist:
        url["amg"]= """<a href="http://www.allmusic.com/cg/amg.dll?opt1=1&P=amg&sql=%s">amg</a> """ % (artist,)
        url["lastfm"]= """<a href="http://www.last.fm/music/%s">lfm</a> """%artist.replace(" ","+")
        
        if title:
            url["lyrc"]="""<a href="http://lyrc.com.ar/en/tema1en.php?%s">lyrics</a> """%urlencode({'artist': artist, 'songname': title})
            #~ url["findlyrics"]="""<a href="http://www.findlyrics.com/%s/%s/">l2</a> """%(artist.replace(" ","_"),title.replace(" ","_"))
            #~ url["lyriki"]="""<a href="http://www.lyriki.com/%s:%s">l3</a> """%(artist.replace(" ","_"),title.replace(" ","_"))
    
    return url

###############################################################################
class AjaxMethods:
    def ajax_player(self, isForced=0, rsrnd=0):
        global MPD
        yield "[[zonePlayer]]"
        
        stat=MPD.status()
        #~ for i in  ['elapsedTime', 'playlist', 'playlistLength', 'random', 'repeat', 'song', 'state', 'stateStr', 'totalTime', 'volume']:
          #~ print i, getattr(stat,i)
        
        if not stat:
            MPD.stop()
            yield "Error : Can't play that!"
            class stat:
                state=0
        else:
            if stat.state in (2,3): # in play/pause
                # aff title
                s = MPD.getCurrentSong()
                if s.path.lower().startswith("http://"):
                    # radio
                    yield "[Stream] "
                    yield s.title and s.title or "playing ..."
                else:
                    # file
                    yield MPD.display(s, config.TAG_FORMAT)
                yield "<br />"
                d = getUrlsForMpdSong(s)
                urls = " ".join([d[i] for i in sorted(d.keys())])
                
                # aff position
                ds = lambda t: "%02d:%02d" % (t/60,t%60)
                s,t,p = MPD.getSongPosition()
                yield """
                  <table>
                    <tr>
                      <td>
                        <a id='sb' onclick='seekclick(event);'>
                            <div id='sbc' style='width:%dpx'></div>
                        </a>
                      </td>
                      <td>
                        %d %% - %s/%s - %s
                      </td>
                    </tr>
                  </table>""" % (int(p*2),int(p),ds(s),ds(t),urls)
        
        yield """
        <button onclick='do_operation("prev");'><<</button>
        """
        if stat.state!=2:
            yield """ <button onclick='do_operation("play");'>></button>"""
        else:
            yield """ <button onclick='do_operation("pause");'>||</button>"""
        if stat.state!=1:
            yield """ <button onclick='do_operation("stop");'>[]</button>"""
        yield """
        <button onclick='do_operation("next");'>>></button>
        """
        
        if stat.state!=0:
            yield """
            <button onclick='do_operation("voldown");'>-</button>
            <button onclick='do_operation("volup");'>+</button>
            """
            yield str(stat.volume)
            yield "%"
        
        if isForced or MPD.needRedrawPlaylist():
            idx,tot = MPD.getPlaylistPosition()
            yield "[[zonePlayList]]"
            yield """
            <h2>Playlist (%d)
            <button onclick='do_operation("clear");'>clear</button>
            <button onclick='do_operation("shuffle");'>shuffle</button>
            </h2>
            """ % tot
            
            l = MPD.playlist()
            for s in l:
                i=l.index(s)
                
                if i+1 == idx:
                    classe = " class='s'"
                else:
                    classe = i%2==0 and " class='p'" or ''
                
                if s.path.lower().startswith("http://"):
                    title = s.path
                else:
                    title = MPD.display(s,CFG.server.tagformat)
                
                yield "<li%s>"%classe
                yield "%03d" % (i+1)
                yield """<a href='#' onclick="do_operation('delete','"""+str(i)+"""');"><span>X</span></a>"""
                yield """<a href='#' onclick="do_operation('play','"""+str(i)+"""');">"""+title+"""</a>"""
                yield "</li>"
    
    def ajax_ope(self, op, idx=None, rsrnd=0):
        if op=="play":
            if idx:
                MPD.play(int(idx))
            else:
                MPD.play()
        elif op=="delete":
            MPD.delete([int(idx),])
        elif op=="next":
            MPD.next()
        elif op=="prev":
            MPD.prev()
        elif op=="play":
            MPD.play()
        elif op=="pause":
            MPD.pause()
        elif op=="stop":
            MPD.stop()
        elif op=="clear":
            MPD.clear()
        elif op=="shuffle":
            MPD.shuffleIt()
        elif op=="seek":
            MPD.seek(percent=int(idx))
        elif op=="volup":
            MPD.volumeUp()
        elif op=="voldown":
            MPD.volumeDown()
        elif op=="changeDisplay":
            MPD.changeDisplay(int(idx))
        else:
            raise "ERROR:"+op+","+str(idx)
        return self.ajax_player()
    
    def ajax_listen(self, file_enc, rsrnd=0):
        file = u64dec(file_enc)
        yield """[[zoneView]]"""
        
        url="listen/%s" % file_enc
        yield """<a href="%s">%s</a> """ % (url,file)
        
        yield """
        <object type="application/x-shockwave-flash"
        data="dewplayer.swf?son=%(url)s&amp;autoplay=1&amp;bgcolor=FFFFFF"
        height="20"
        width="160">
        <param name="movie" value="dewplayer.swf?son=%(url)s&amp;autoplay=1&amp;bgcolor=FFFFFF">
        </object>
        """ % locals()
    

###############################################################################
def main():
    global MPD
    MPD = MpdSafe(config.MPD_HOST,config.MPD_PORT)
    err = MPD.connect()
    if err:
        print "wymypy can't connect to your MPD : ",err
        sys.exit(-1)
    else:
        app = WyMyPy(wPlugin.get_instances(MPD))
        print "wymypy is listening on http://localhost:%s/" % (config.HTTP_PORT)
        print "(hit CTRL+C to quit)"
        try:
            wsgiserver.WSGIServer(('', config.HTTP_PORT), {'': app}).serve_forever()
        except socket.error:
            print "The port %s is already in use, perhaps wymypy is already running ?!" % config.HTTP_PORT
            sys.exit(-1)
        sys.exit(0)

if __name__=="__main__":
    USAGE = """USAGE : %s [option]
    Webserver frontend for MusicPlayerDaemon. Version """+__version__+"""
    Copyright 2007 by Marc Lentz under the GPL2 licence.
    Options:
        -h        : this help"""
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "":
            main()
        else:
            print USAGE % os.path.basename(sys.argv[0])
            sys.exit(-1)
    else:
        main()
