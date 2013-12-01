from wymypy.plugins import wPlugin

class PlayLists(wPlugin):
    def init(self):
        self.button_index = 2
    
    def show(self):
        return """
            <button onclick='ajax_listePL()'>Playlists</button>
        """
    
    def ajax_listePL(self):
        yield "<h2>Playlists</h2>"
        l = self.mpd.getPlaylistNames()
        for i in l:
            classe = l.index(i) % 2 == 0 and " class='p'" or ''
            yield "<li%s>" % classe
            yield """<a href='#' onclick='ajax_playPL("%s");'><span>></span></a>""" % (i.path,)
            yield i.path
            yield "</li>"
    
    def ajax_playPL(self, pl):
        self.mpd.load(pl)
        return "player"  # tell to update player
