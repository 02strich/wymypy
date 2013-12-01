import os


class Library(object):
    def __init__(self, mpd, config):
        self.config = config
        self.mpd = mpd
        self.button_index = 1

    def show(self):
        return """
            <button onclick='ajax_library("")'>Library</button>
        """

    def ajax_library(self, dir):
        go_library = lambda link, aff: """<a href="#" onclick='ajax_library("%s")'>%s</a>""" % (link, aff)
        go_add = lambda f: """<a href='#' onclick='ajax_ladd("%s");'>%s</a>""" % (f, "<span>&gt;</span>")
        if dir != "":
            yield "<h2>"
            path = ""
            yield go_library("", "Library")
            for i in dir.split("/"):
                yield " / "
                if path != "":
                    path += "/"
                path += i
                if path != dir:
                    yield go_library(path, i)
                else:
                    yield i
            yield go_add(dir)
            yield "</h2>"
        else:
            yield "<h2>Library</h2>"

        l = self.mpd.ls([dir], onlyDirs=True)
        l.sort(cmp=lambda a, b: cmp(a.lower(), b.lower()))
        c = 0
        for s in l:
            classe = (c % 2 == 0) and " class='p'" or ''
            yield "<li%s>" % classe
            yield go_library(s, os.path.basename(s))
            yield "</li>"
            c += 1

        l = self.mpd.ls([dir], onlyFiles=True)
        l.sort(cmp=lambda a, b: cmp(a.lower(), b.lower()))
        for s in l:
            classe = (c % 2 == 0) and " class='p'" or ''
            yield "<li%s>" % classe
            yield go_add(s)
            yield self.go_listen(s)
            yield os.path.basename(s)
            yield "</li>"
            c += 1

    def ajax_ladd(self, f):
        self.mpd.add([f, ])
        return "player"  # tell to update player
