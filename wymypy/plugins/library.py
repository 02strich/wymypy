import os

from flask import render_template_string

class Library(object):
    has_panel = True
    button_index = 1
    button_label = "Library"

    index_template = """
<h2>
    {% for path_element in path %}
        <a href="#" onclick='load_plugin_content("library", "index", {path: "{{ "/".join(path[:loop.index]) }}"})'>{{ path_element }}</a>
        {% if not loop.last %}/{% else %}
            <a href="#" onclick='execute_plugin("library", "add", {file_name: "{{ path|join("/") }}"}, refresh_player);'><span>></span></a>
        {% endif %}
    {% else %}
        Library
    {% endfor %}
</h2>

{% for dir in dirs %}
    <li {{ loop.cycle("", "class='p'") }}><a href="#" onclick="load_plugin_content('library', 'index', {path: '{{ dir }}'});">{{ basename(dir) }}</a></li> 
{% endfor %}

{% for file in files %}
    <li {{ loop.cycle("", "class='p'") }}><a href="#" onclick='execute_plugin("library", "add", {file_name: "{{ file }}"}, refresh_player);'>{{ basename(file) }}</a></li> 
{% endfor %}
"""

    def __init__(self, mpd, config):
        self.config = config
        self.mpd = mpd

    def index(self, path=""):
        return render_template_string(self.index_template, basename=os.path.basename, path=path.split("/") if path else [], dirs=self.mpd.ls([path], onlyDirs=True), files=self.mpd.ls([path], onlyFiles=True))

    def ajax_add(self, file_name):
        self.mpd.add([file_name, ])
