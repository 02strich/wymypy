import logging
import time
import threading
import urllib2

from flask import render_template_string

try:
    from go_gae_proxy import GoProxyHandler
except:
    pass

from pandora import Pandora as PandoraPython
from pandora.connection import AuthenticationError

logger = logging.getLogger(__name__)


class WorkerThread(threading.Thread):
    def __init__(self, MPD, pandora):
        threading.Thread.__init__(self)
        self.mpd = MPD
        self.pandora = pandora
        self.shouldDie = False
        self.retry = False

    def run(self):
        while not self.shouldDie:
            try:
                idx, tot = self.mpd.getPlaylistPosition()
                #logger.debug("pandora_worker - tot: %d idx: %d", tot, idx)

                if tot - idx < 3:
                    for i in range(0, 2):
                        try:
                            song = self.pandora.get_next_song()
                            self.retry = False
                        except Exception, e:
                            if not self.retry:
                                self.retry = True
                                self.pandora.authenticate(username=config.PANDORA_USERNAME, password=config.PANDORA_PASSWORD)
                                song = self.pandora.get_next_song()
                            else:
                                logger.exception(e)
                        self.mpd.add([str(song['audioUrlMap']['highQuality']['audioUrl'])])
                time.sleep(5)
            except Exception, e:
                logger.exception(e)


class Pandora2(object):
    has_panel = True
    button_index = 51
    button_label = "Pandora"
    index_template = """
<h2>Pandora Radio</h2>

Current station: {{ current_station_name }}

<button id="pandora_stop" style="display: {% if playing %}inline{% else %}none{% endif %};" onclick='execute_plugin("pandora2", "stop", {}); $("#pandora_stop").hide(); $("#pandora_play").show();'>[]</button>
<button id="pandora_play" style="display: {% if playing %}none{% else %}inline{% endif %};" onclick='execute_plugin("pandora2", "play", {}); $("#pandora_play").hide(); $("#pandora_stop").show();'>></button>

{% for station in stations %}
    <li 
    {% if station['stationId'] == current_station_id %}
        class='s'
    {% else %}
        {{ loop.cycle("", "class='p'") }}
    {% endif %}><a href="#" onclick='load_plugin_content("pandora2", "switch_station", {stationId: "{{ station['stationId'] }}"});'>{{ station['stationName'].replace("'", "") }}</a></li> 
{% endfor %}

<br/>
<a href='#' onclick='load_plugin_content("pandora2", "reload_station_list", {});'>Reload station list</a>
"""

    def __init__(self, mpd, config):
        self.config = config
        self.mpd = mpd

        # setup proxy
        if "proxy" in self.config:
            if self.config['proxy'].startswith("gae://") or self.config['proxy'].startswith('gaes://'):
                proxy_support = GoProxyHandler("http" + self.config['proxy'][3:])
            else:
                proxy_support = urllib2.ProxyHandler({"http" : self.config['proxy'], 'https': self.config['proxy']})
            opener = urllib2.build_opener(proxy_support)
            urllib2.install_opener(opener)

        # setup pandora
        self.pandora = PandoraPython()
        if not self.pandora.authenticate(username=self.config.get("username", ""), password=self.config.get("password", "")):
            raise ValueError("Wrong pandora credentials or proxy supplied")

        self.current_station = {}
        self.playing = False

    def index(self):
        return render_template_string(self.index_template, current_station_name=self.current_station.get("stationName", ""), current_station_id=self.current_station.get("stationId", ""), playing=self.playing, stations=self.pandora.stations)

    def reload_station_list(self):
        self.pandora.update_station_list()
        return self.index()

    def switch_station(self, stationId):
        for station in self.pandora.stations:
            if station['stationId'] == stationId:
                self.current_station = station
                break

        try:
            self.pandora.switch_station(self.current_station)
        except Exception, e:
            self.pandora.authenticate(username=self.config.get("username", ""), password=self.config.get("password", ""))
            self.pandora.switch_station(self.current_station)
            logger.exception(e)

        return self.index()

    def ajax_play(self):
        if self.current_station:
            self.worker = WorkerThread(self.mpd, self.pandora)
            self.worker.daemon = True
            self.worker.start()
            self.playing = True

    def ajax_stop(self):
        self.worker.shouldDie = True
        self.worker.join()
        self.playing = False
