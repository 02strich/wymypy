from couchdbkit import *
from flask import render_template_string


class Greeting(Document):
    url = StringProperty()


class Iradio(object):
    has_panel = True
    button_index = 50
    button_label = "iRadio"
    index_template = """
<h2>Internet Radio</h2>
{% for radio in docs %}
    <li {{ loop.cycle("", "class='p'") }}>
        <a href='#' onclick='load_plugin_content("iradio", "delete", {document_id: "{{ radio["_id"] }}" });'><span>X</span></a>
        <a href="#" onclick='execute_plugin("iradio", "play", {url: "{{ radio['url'] }}"}, refresh_player);'>{{ radio['url'] }}</a>
    </li> 
{% endfor %}

<h3>Add Internet Station:
    <form onsubmit='load_plugin_content("iradio", "add", {url: $("#iradio_url").val()});return false'>
        <input type='text' id='iradio_url' size="10"/>
        <button type='submit'>add</button>
    </form>
</h3>
"""

    def __init__(self, mpd, config):
        self.config = config
        self.mpd = mpd

        self.server = Server(uri=self.config.get("couchdb_url", ""))
        self.db = self.server.get_or_create_db("mpd_radio")

    def index(self):
        return render_template_string(self.index_template, docs=[self.db.get(i['id']) for i in self.db.all_docs().all()])

    def add(self, url=None):
        self.db.save_doc({'url': url})
        return self.index()

    def delete(self, document_id=None):
        self.db.delete_doc(document_id)
        return self.index()

    def ajax_play(self, url):
        self.mpd.add([url])
