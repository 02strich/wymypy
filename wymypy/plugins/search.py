import os

from flask import render_template_string


class Search(object):
    has_panel = True
    button_index = 100
    button_label = ""
    button_html = """
        <form onsubmit='load_plugin_content("search", "index", {search_type: $("#tq").val(), term:$("#q").val()}); return false'>
            <input type='text' id='q' size="10"/>
            <select id='tq'>
                <option value='filename'>filename</option>
                <option value='artist'>artist</option>
                <option value='album'>album</option>
                <option value='title'>title</option>
            </select>
            <button type='submit'>Search</button>
        </form>
    """

    index_template = """
<h2> Search for '{{ term }}' in {{ search_type }}</h2>

{% for result in results %}
    <li {{ loop.cycle("", "class='p'") }}><a href="#" onclick='execute_plugin("search", "add", {file_name: "{{ result }}"}, refresh_player);'>{{ result }}</a></li> 
{% endfor %}
"""

    def __init__(self, mpd, config):
        self.config = config
        self.mpd = mpd

    def index(self, term, search_type):
        print repr(search_type)
        return render_template_string(self.index_template, term=term, search_type=search_type, results=self.mpd.search(search_type, term))

    def ajax_add(self, file_name):
        self.mpd.add([file_name, ])
