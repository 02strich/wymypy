import os


class Search(object):
    def __init__(self, mpd, config):
        self.config = config
        self.mpd = mpd

    def show(self):
        return """
            <form onsubmit='ajax_search($("tq").value,$("q").value);return false'>
            <input type='text' id='q' size="10"/>
            <select id='tq'>
                <option value='filename'>filename</option>
                <option value='artist'>artist</option>
                <option value='album'>album</option>
                <option value='title'>title</option>
            </select>
            <button type='submit'>search</button>
            </form>
        """

    def ajax_search(self, tq, q):
        q = q.strip()
        yield "<h2>Search for '"
        yield q
        yield "' in "
        yield tq
        yield "</h2>"
        if len(q) > 1:
            l = self.mpd.search(tq, q)
            for i in l:
                p = os.path.dirname(i)
                f = os.path.basename(i)
                classe = l.index(i) % 2 == 0 and " class='p'" or ''
                yield "<li%s>" % classe
                yield """<a href='#' onclick='ajax_add("%s");'>%s</a>""" % (i, "<span>></span>")
                yield self.go_listen(i)
                yield f
                #~ yield "<br />"
                #~ yield go_library(p,p)
                yield "</li>"

    def ajax_add(self, f):
        self.mpd.add([f, ])
        return "player"  # tell to update player
