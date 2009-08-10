#!/usr/bin/env python
# -*- coding: utf-8 -*-
import mpdclient
import os

def protect(ret=None):
    def decorator(func):
        def wrapper(*__args,**__kw):
            try:
                protect.instance.connect()
                return func(*__args,**__kw)
            except mpdclient.MpdError,m:
                return ret
        return wrapper
    return decorator


class MpdSafe:

    def __init__(self,host,port):
        self.__cnx=None
        self.__host=host
        self.__port=port
        protect.instance = self

        self.__current=None
        self.__prec=None
        self.__dispTags=False  # disp filenames

    def connect(self):
        try:
            self.__cnx = mpdclient.MpdController(self.__host,self.__port)
            return ""
        except Exception,m:
            return m

    def needRedrawPlaylist(self):
        return self.__current != self.__prec

    @protect(None)
    def status(self):
        stat = self.__cnx.status()
        self.__prec = self.__current
        self.__current = (stat.song,stat.playlistLength)
        return stat

    @protect(None)
    def getCurrentSong(self):
        return self.__cnx.getCurrentSong()

    @protect((0,0,1))
    def getSongPosition(self):
        return self.__cnx.getSongPosition()

    @protect((0,0))
    def getPlaylistPosition(self):
        return self.__cnx.getPlaylistPosition()

    @protect([])
    def playlist(self):
        return self.__cnx.playlist()

    @protect([])
    def getPlaylistNames(self):
        return self.__cnx.getPlaylistNames()

    @protect([])
    def search(self,tq,q):
        return self.__cnx.search(tq, q)

    @protect([])
    def ls(self, dirs, onlyFiles=False, onlyDirs=False):
        return self.__cnx.ls(dirs,onlyFiles=onlyFiles, onlyDirs=onlyDirs)

    @protect([])
    def listall(self,*dirs):
        return self.__cnx.listall(*dirs)

    @protect()
    def seek(self, percent=None, seconds=None):
        self.__cnx.seek(percent=percent, seconds=seconds)

    @protect()
    def play(self,i=None):
        if i!=None:
            self.__cnx.play(i)
        else:
            self.__cnx.play()

    @protect()
    def delete(self,l):
        self.__cnx.delete(l)

    @protect()
    def next(self):
        self.__cnx.next()

    @protect()
    def prev(self):
        self.__cnx.prev()

    @protect()
    def pause(self):
        self.__cnx.pause()

    @protect()
    def stop(self):
        self.__cnx.stop()

    @protect()
    def clear(self):
        self.__cnx.clear()

    @protect()
    def shuffleIt(self):
        self.__cnx.shuffle()

    @protect()
    def load(self,pl):
        self.__cnx.load(pl)

    @protect()
    def add(self,l):
        assert type(l)==list
        self.__cnx.add(l)

    @protect()
    def volumeUp(self):
        stat=self.__cnx.status()
        self.__cnx.volume(min(100,stat.volume+5))

    @protect()
    def volumeDown(self):
        stat=self.__cnx.status()
        self.__cnx.volume(max(0,stat.volume-5))

    def changeDisplay(self,checked):
        self.__dispTags = (checked == 1)
        self.__current = None           # force redraw playlist

    def display(self,s,format="<b>%(artist)s</b> - %(title)s"):
        assert type(s) == mpdclient.Song
        if self.__dispTags:
            artist = s.artist
            album = s.album
            title = s.title
            path = s.path
            track = s.track

            atLessOne = False
            if format.find("(artist)")>0 and artist.strip()!="":
              atLessOne = True
            else:
              if format.find("(title)")>0 and title.strip()!="":
                atLessOne = True
              else:
                if format.find("(album)")>0 and album.strip()!="":
                  atLessOne = True
                else:
                  if format.find("(track)")>0 and track.strip()!="":
                    atLessOne = True
            if atLessOne:
              return format % locals()
            else:
              return "<font color='red'>"+os.path.basename(s.path)+"</font>"
        else:
            return os.path.basename(s.path)


if __name__ == "__main__":
    pass
