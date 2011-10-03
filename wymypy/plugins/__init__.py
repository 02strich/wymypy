#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import inspect
import traceback

import config

class wPlugin(object):
    # attributs instance
    path = property(lambda self: self.__class__.__name__)
    css = ""
    js = ""
    
    def __init__(self, mpd):
        self.mpd = mpd
        self.button_index = 99
        self.init()
    
    def init(self):  # to override
        pass
    
    def show(self):  # to override
        pass
    
    def index(self):
        pass
    
    # for both library and search plugins
    def go_listen(self, file):
        """ Draw a "Listen now button" for mp3 files """
        if file[-4:].lower() == ".mp3":
            return """<a href="#" onclick='ajax_listen("%s")'><span>V</span></a>""" % file
        else:
            return ""
    
    @staticmethod
    def get_instances(mpd):
        """ instanciate classes which inherits of me, return the list """
        instances = {}
        cwd = os.path.abspath(os.path.dirname(__file__))
        
        for directory in os.listdir(cwd):
            if not os.path.isdir(os.path.join(cwd, directory)): continue
            if directory in config.BANNED_PLUGINS: continue
            
            try:
                __import__("plugins.%s" % directory)
            except Exception, m:
                print "Plugin import error for [%(name)s]: %(error)s" % {'name': directory, 'error': m}
                traceback.print_exc()
                continue
            
            plugin_module = sys.modules["plugins.%s" % directory]
            for name in dir(plugin_module):
                current_class = getattr(plugin_module, name)
                if not inspect.isclass(current_class):
                    continue
                
                try:
                    isPlugin = issubclass(current_class, wPlugin) and current_class != wPlugin
                except Exception, m:
                    isPlugin = False
                
                if isPlugin:
                    print " - load plugin", directory
                    try:
                        instances[directory] = current_class(mpd)
                    except Exception, m:
                        print "Plugin instanciate error for", directory, ":", m
                        traceback.print_exc()
        return instances

if __name__ == "__main__":
    class FakeMpd:
        def listall(self, a):
            return []
    print wPlugin.get_instances(FakeMpd())
