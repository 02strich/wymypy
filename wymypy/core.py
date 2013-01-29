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
import os
import sys

import config
from libs.mpdsafe import MpdSafe
from plugins import wPlugin

from flask import Flask, render_template, request
from werkzeug.serving import WSGIRequestHandler
app = Flask(__name__)
app.config.from_object(config)

@app.template_filter('ifnotnone')
def ifnotnone_filter(s):
	if s == None:
		return ""
	else:
		return s

@app.route('/')
def root():
	return render_template('main.html', plugins=sorted(app.plugins.values(), key=lambda plugin: plugin.button_index))

@app.route('/player')
def player():
	return render_template('player.html')


@app.route('/plugins.css')
def plugins_css():
	rv = app.make_response('\n'.join([i.css for i in app.plugins.values()]))
	rv.mimetype = 'text/css'
	return rv


@app.route('/plugins.js')
def plugins_js():
	result = ""
	
	def register_ajax(path, method):
		return """function ajax_%(method)s() { sajax_do_call("%(path)s%(method)s", ajax_%(method)s.arguments);}""" % locals()
	
	# plugins ajax
	for plugin in app.plugins.values():
		result += '\n'.join([register_ajax("/__ajax/" + plugin.path + "/", i[5:]) for i in dir(plugin) if(str(i).lower().startswith("ajax_") )])
	
	# plugins 'normal' js
	result += '\n'.join([i.js for i in app.plugins.values()])
	
	rv = app.make_response(result)
	rv.mimetype = 'text/javascript'
	return rv


@app.route('/__ajax/<method>', methods=["GET", "POST"])
@app.route('/__ajax/<plugin>/<method>', methods=["GET", "POST"])
def make_ajax(method, plugin=None):
	inst = app.plugins[plugin.lower()]
	method = "ajax_" + method
	arg = [str(a) for a in request.form.values()]
	
	if hasattr(inst, method):
		fct = getattr(inst, method)
		iter = fct(*(arg), **({}))
		
		if plugin.lower() != "player":
			if "'generator'" in str(type(iter)):
				def _iterInZoneView(iter):
					yield "[[zoneView]]"
					for i in iter:
						yield i
				iter = _iterInZoneView(iter)
			else:
				if iter == "player":  # plugin ajax method returns "player" -> redraw player
					inst = app.plugins['player']
					iter = inst.ajax_player()
				else:
					return """+ {"":""}"""
		
		dic = flux2dict(iter)
		# print "AJAXCALL:",method,arg,"--->",dic.keys()
		response = "+ " + jsonize(dic)
		
		# set cach-control header for Safari on iOS 6
		return (response, 200, {"Cache-Control": "no-cache"})
	else:
		return "- methode non existent: ", method


@app.route('/plugin/<plugin>', methods=["GET", "POST"])
@app.route('/plugin/<plugin>/<method>', methods=["GET", "POST"])
def plugin_methods(plugin, method=None):
	inst = app.plugins[plugin.lower()]
	arg = [str(a) for a in request.form.values()]
	
	if method == None:
		return inst.index()
	else:
		if hasattr(inst, method):
			fct = getattr(inst, method)
			return fct(*(arg), **({}))
		else:
			return "- methode non existent: ", method
	

def flux2dict(iter):
    l = {}
    key = None
    for i in iter:
        if i[:2] == "[[" and i[-2:] == "]]":
            key = i[2:-2]
            l[key] = ""
        else:
            if key == None:
                raise "key error"
            else:
                l[key] += i
    return l


def jsonize(dict):
    return "{" + ",".join([""" "%s" : "%s" """ % (i, dict[i].replace('"', '\\"').replace('\n', '\\n')) for i in dict]) + "}"



###############################################################################
class WyMyPyRequestHandler(WSGIRequestHandler):
	wbufsize = -1

def main():
	# connect to MPD
	MPD = MpdSafe(config.MPD_HOST, config.MPD_PORT)
	err = MPD.connect()
	if err:
		print "wymypy can't connect to your MPD : ", err
		sys.exit(-1)
		
	# configure logging
	if hasattr(config, "LOGGING"):
		import logging
		hdlr = logging.FileHandler(config.LOGGING)
		formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
		hdlr.setFormatter(formatter)
		app.logger.addHandler(hdlr)
	MPD.logger = app.logger
	
	# configure app
	app.MPD = MPD
	app.plugins = wPlugin.get_instances(MPD)
	
	# start server
	app.run(host=app.config['SERVER_IFACE'], port=app.config['SERVER_PORT'], request_handler=WyMyPyRequestHandler)

if __name__ == "__main__":
	main()

