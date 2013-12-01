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
                           plugins=sorted(app.plugins.values(), key=lambda plugin: plugin.button_index))


@app.route('/player')
def player():
    return render_template('player.html')


@app.route('/plugins.css')
def plugins_css():
    response = app.make_response('\n'.join([i.css for i in app.plugins.values()]))
    response.mimetype = 'text/css'
    return response


@app.route('/plugins.js')
def plugins_js():
    result = ""

    def register_ajax(path, method):
        return """function ajax_%(method)s() { sajax_do_call("%(path)s%(method)s", ajax_%(method)s.arguments);}""" % locals()

    # plugins ajax
    for plugin in plugins.values():
        result += '\n'.join([register_ajax("/__ajax/" + plugin.path + "/", i[5:]) for i in dir(plugin) if(str(i).lower().startswith("ajax_"))])

    # plugins 'normal' js
    result += '\n'.join([i.js for i in plugins.values()])

    response = app.make_response(result)
    response.mimetype = 'text/javascript'
    return response


@app.route('/__ajax/<method>', methods=["GET", "POST"])
@app.route('/__ajax/<plugin>/<method>', methods=["GET", "POST"])
def ajax_methods(method, plugin=None):
    # right now the core has no ajax methods
    if plugin is None:
        abort(404)

    # process plugin ajax methods
    inst = app.plugins[plugin.lower()]
    arg = [str(a) for a in request.form.values()]

    if hasattr(inst, "ajax_" + method):
        result = getattr(inst, "ajax_" + method)(*arg)

        # set cach-control header for Safari on iOS 6
        response = app.make_response(json.dumps(result))
        response.headers["Cache-Control"] = "no-cache"
        return response

    abort(404)


@app.route('/plugin/<plugin>', methods=["GET", "POST"])
@app.route('/plugin/<plugin>/<method>', methods=["GET", "POST"])
def plugin_methods(plugin, method=None):
    inst = plugins[plugin.lower()]
    arg = [str(a) for a in request.form.values()]

    if method is None:
        return app.make_response(inst.index(*arg))

    if hasattr(inst, method):
        return app.make_response(getattr(inst, method)(*arg))

    abort(404)
