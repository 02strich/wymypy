#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#	   wymypy.py
#
#	   Copyright 2007 Marc Lentz <manatlan@gmail.com>
#
#	   This program is free software; you can redistribute it and/or modify
#	   it under the terms of the GNU General Public License as published by
#	   the Free Software Foundation; either version 2 of the License, or
#	   (at your option) any later version.
#
#	   This program is distributed in the hope that it will be useful,
#	   but WITHOUT ANY WARRANTY; without even the implied warranty of
#	   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#	   GNU General Public License for more details.
#
#	   You should have received a copy of the GNU General Public License
#	   along with this program; if not, write to the Free Software
#	   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
import wymypy.config
from wymypy.plugins import wPlugin

class Player(wPlugin):	  
	def ajax_player(self, isForced=0):
		yield "[[zonePlayer]]"

		stat = self.mpd.status()
		#~ for i in	 ['elapsedTime', 'playlist', 'playlistLength', 'random', 'repeat', 'song', 'state', 'stateStr', 'totalTime', 'volume']:
		  #~ print i, getattr(stat,i)

		if not stat:
			self.mpd.stop()
			yield "Error : Can't play that!"

			class stat:
				state = 0
		else:
			if stat.state in (2, 3):  # in play/pause
				# aff title
				s = self.mpd.getCurrentSong()
				if s.path.lower().startswith("http://"):
					# radio
					yield "[Stream] "
					yield s.title and s.title or "playing ..."
				else:
					# file
					yield self.mpd.display(s, wymypy.config.TAG_FORMAT)
				yield "<br />"
				
				# aff position
				ds = lambda t: "%02d:%02d" % (t / 60, t % 60)
				s, t, p = self.mpd.getSongPosition()
				yield """
				  <table>
					<tr>
					  <td>
						<a id='sb' onclick='seekclick(event);'>
							<div id='sbc' style='width:%dpx'></div>
						</a>
					  </td>
					  <td>
						%d %% - %s/%s
					  </td>
					</tr>
				  </table>""" % (int(p * 2), int(p), ds(s), ds(t))

		yield """
		<button onclick='ajax_ope("prev");'><<</button>
		"""
		if stat.state != 2:
			yield """ <button onclick='ajax_ope("play");'>></button>"""
		else:
			yield """ <button onclick='ajax_ope("pause");'>||</button>"""
		if stat.state != 1:
			yield """ <button onclick='ajax_ope("stop");'>[]</button>"""
		yield """
		<button onclick='ajax_ope("next");'>>></button>
		"""

		if stat.state != 0:
			yield """
			<button onclick='ajax_ope("voldown");'>-</button>
			<button onclick='ajax_ope("volup");'>+</button>
			<button onclick='ajax_ope("mute");'>@</button>
			"""
			yield str(stat.volume)
			yield "%"

		if isForced or self.mpd.needRedrawPlaylist():
			idx, tot = self.mpd.getPlaylistPosition()
			yield "[[zonePlayList]]"
			yield """
			<h2>Playlist (%d)
			<button onclick='ajax_ope("clear");'>clear</button>
			<button onclick='ajax_ope("clear_old");'>clear old</button>
			<button onclick='ajax_ope("shuffle");'>shuffle</button>
			</h2>
			""" % tot

			l = self.mpd.playlist()
			for s in l:
				i = l.index(s)

				if i + 1 == idx:
					classe = " class='s'"
				else:
					classe = i % 2 == 0 and " class='p'" or ''

				if s.path.lower().startswith("http://"):
					title = s.path
				else:
					title = self.mpd.display(s, wymypy.config.TAG_FORMAT)

				yield "<li%s>" % classe
				yield "%03d" % (i + 1)
				yield """<a href='#' onclick="ajax_ope('delete','""" + str(i) + """');"><span>X</span></a>"""
				yield """<a href='#' onclick="ajax_ope('play','""" + str(i) + """');">""" + title + """</a>"""
				yield "</li>"
	
	
	def ajax_ope(self, op, idx=None):
		if op == "play":
			if idx:
				self.mpd.play(int(idx))
			else:
				self.mpd.play()
		elif op == "delete":
			self.mpd.delete([int(idx), ])
		elif op == "next":
			self.mpd.next()
		elif op == "prev":
			self.mpd.prev()
		elif op == "play":
			self.mpd.play()
		elif op == "pause":
			self.mpd.pause()
		elif op == "stop":
			self.mpd.stop()
		elif op == "clear":
			self.mpd.clear()
		elif op == "clear_old":
			idx, tot = self.mpd.getPlaylistPosition()
			self.mpd.delete([[0, max(0, idx-2)]])
		elif op == "shuffle":
			self.mpd.shuffleIt()
		elif op == "seek":
			self.mpd.seek(percent=int(idx))
		elif op == "volup":
			self.mpd.volumeUp()
		elif op == "voldown":
			self.mpd.volumeDown()
		elif op == "mute":
			self.mpd.mute()
		elif op == "changeDisplay":
			self.mpd.changeDisplay(int(idx))
		else:
			raise "ERROR:" + op + "," + str(idx)
		return self.ajax_player()