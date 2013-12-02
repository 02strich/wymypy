from flask import render_template_string

class Playlists(object):
    has_panel = True
    button_index = 2
    button_label = "Playlists"
    index_template = """
<h2>Playlists</h2>

{% for playlist in playlists %}
    <li {{ loop.cycle("", "class='p'") }}><a href="#" onclick='execute_plugin("playlists", "load", {playlist: "{{ playlist.path }}"}, refresh_player);'>{{ playlist.path }}</a></li> 
{% endfor %}
"""

    def __init__(self, mpd, config):
        self.config = config
        self.mpd = mpd

    def index(self):
        return render_template_string(self.index_template, playlists=self.mpd.getPlaylistNames())

    def ajax_load(self, playlist):
        self.mpd.load(playlist)
