from flask import make_response
from string import Template


class CiscoRadio(object):
    def index(self):
        resp = make_response(Template("""<CiscoIPPhoneMenu>
<Title>WyMyPy</Title>
<Prompt>Play Music NOW !</Prompt>
<MenuItem>
    <Name>Play - Pause</Name>
    <URL>http://$server/plugin/cisco/playpause</URL>
</MenuItem>
<MenuItem>
    <Name>Stop</Name>
    <URL>http://$server/plugin/cisco/stop</URL>
</MenuItem>
<MenuItem>
    <Name>Volume Up</Name>
    <URL>http://$server/plugin/cisco/volup</URL>
</MenuItem>
<MenuItem>
    <Name>Volume Down</Name>
    <URL>http://$server/plugin/cisco/voldown</URL>
</MenuItem>
<MenuItem>
    <Name>Next</Name>
    <URL>http://$server/plugin/cisco/next</URL>
</MenuItem>
<MenuItem>
    <Name>Previous</Name>
    <URL>http://$server/plugin/cisco/prev</URL>
</MenuItem>
</CiscoIPPhoneMenu>""").substitute(server=config.SERVER_NAME), 200)
        resp.headers['Content-type'] = 'text/xml'
        resp.headers['Connection'] = 'close'
        resp.headers['Expires'] = '-1'
        return resp
    
    def playpause(self):
        self.mpd.pause()
        return self.index()
    
    def stop(self):
        self.mpd.stop()
        return self.index()
    
    def next(self):
        self.mpd.next()
        return self.index()
    
    def prev(self):
        self.mpd.prev()
        return self.index()
    
    def volup(self):
        self.mpd.volumeUp()
        return self.index()
    
    def voldown(self):
        self.mpd.volumeDown()
        return self.index()