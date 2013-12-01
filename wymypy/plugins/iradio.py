from couchdbkit import *


class Greeting(Document):
    url = StringProperty()


class Iradio(object):
    def __init__(self, mpd, config):
        self.config = config
        self.mpd = mpd

        self.button_index = 50
        self.server = Server(uri=self.config.get("couchdb_url", ""))
        self.db = self.server.get_or_create_db("mpd_radio")

    def show(self):
        return """
            <button onclick='ajax_radio()'>Radio</button>
        """

    def ajax_radio(self, ignore=0):
        yield "<h2>Internet Radio</h2>"

        # list stations
        index = 0
        for i in self.db.all_docs().all():
            cur = self.db.get(i['id'])
            classe = index % 2 == 0 and " class='p'" or ''
            yield "<li%s>" % classe
            yield """<a href='#' onclick='ajax_streamPlay("%s");'><span>></span></a>""" % (cur['url'])
            yield cur['url']
            yield "</li>"
            index += 1

        # add new station
        yield "<h3>Add Internet Station:"
        yield """
          <form onsubmit='ajax_streamAdd($("radio").value);return false'>
            <input type='text' id='radio' size="10"/>
            <button type='submit'>add</button>
          </form>
        """

    def ajax_streamPlay(self, url):
        self.mpd.add([url])
        return "player"

    def ajax_streamAdd(self, f):
        self.db.save_doc({'url': f})
        for ele in self.ajax_radio():
            yield ele
        #return "player"
