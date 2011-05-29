#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys

import base64
u64enc = base64.urlsafe_b64encode
u64dec = base64.urlsafe_b64decode


class wPlugin(object):
    instances=[]

    def __init__(self,mpd):
        self.mpd=mpd
        self.init()

    # attributs instance
    path = property(lambda self: self.__class__.__name__)
    css=""
    js=""

    def init(self): # to override
        pass
    def get(self,path): # to override
        pass

    def go_listen(self,file):
        """ Draw a "Listen now button" for mp3 files """
        if file[-4:].lower()==".mp3":
            return """<a href="#" onclick='ajax_listen("%s")'><span>V</span></a>""" % u64enc(file)
        else:
            return ""

    @classmethod
    def initInstances(cls,mpd,path="."):
        """ instanciate classes which inherits of me, return the list """
        #~ gl={}
        #~ gl.update( globals() )
        #~ l=[i for i in gl.values() if type(i)==type(cls) and i!=cls and issubclass(i,cls)]

        cls = wPlugin
        wPlugin.instances=[]
        for id in os.listdir(path):
            if os.path.isdir(os.path.join(path,id)):
                sys.path.append(path)
                namespace=id
                #~ namespace = path=="." and id or path+"."+id
                #~ print namespace
                try:
                    __import__(namespace)
                except Exception,m:
                    print "Plugin import error for [%s]"%id,":",m
                    continue
                mod = sys.modules[namespace]
                obj =mod.__dict__
                for i in obj:
                    try:
                        isPlugin= issubclass(obj[i],cls) and obj[i]!=cls
                    except Exception,m:
                        isPlugin= False

                    if isPlugin:
                        print " - load plugin", id
                        try:
                            wPlugin.instances.append( obj[i](mpd) )
                        except Exception,m:
                            print "Plugin instanciate error for",id,":",m


    @staticmethod
    def getInstance(n):
        for i in wPlugin.instances:
            if i.__class__.__name__ == n:
                return i


try:
    __builtins__["wPlugin"] = wPlugin
except:
    __builtins__.__dict__["wPlugin"] = wPlugin


if __name__=="__main__":
    class FakeMpd:
        def listall(self,a):
            return []
    wPlugin.initInstances(FakeMpd())
    print wPlugin.instances
