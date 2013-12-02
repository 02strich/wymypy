import ConfigParser
import json

from flask import Flask, render_template, request, abort

from wymypy.libs.mpdsafe import MpdSafe

app = Flask(__name__)
config = ConfigParser.SafeConfigParser()
mpd = MpdSafe()
plugins = []


@app.template_filter('ifnotnone')
def ifnotnone_filter(s):
    if s is None:
        return ""
    else:
        return s


@app.route('/')
def root():
    return render_template('main.html',
                           stream_url=config.get("mpd", "stream") if config.has_option("mpd", "stream") else None,
                           player=plugins['player'].index(),
                           player_playlist=plugins['player'].playlist(),
                           plugins=sorted(plugins.values(), key=lambda plugin: plugin.button_index))


@app.route('/player')
def player():
    return render_template('player.html')


@app.route('/plugin/<plugin>', methods=["GET", "POST"])
@app.route('/plugin/<plugin>/<method>', methods=["GET", "POST"])
def plugin_methods(plugin, method=None):
    inst = plugins[plugin.lower()]
    args = request.form.to_dict()

    if method is None:
        method = "index"

    if hasattr(inst, method):
        return app.make_response(getattr(inst, method)(**args))

    abort(404)


@app.route('/__ajax/<method>', methods=["GET", "POST"])
@app.route('/__ajax/<plugin>/<method>', methods=["GET", "POST"])
def ajax_methods(method, plugin=None):
    # right now the core has no ajax methods
    if plugin is None:
        abort(404)

    # process plugin ajax methods
    inst = plugins[plugin.lower()]
    args = request.form.to_dict()

    if hasattr(inst, "ajax_" + method):
        # set cach-control header for Safari on iOS 6
        response = app.make_response(json.dumps(getattr(inst, "ajax_" + method)(**args)))
        response.headers["Cache-Control"] = "no-cache"
        return response

    abort(404)
