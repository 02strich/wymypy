import inspect
import logging
import os
import os.path
import sys

# fixup sys.path for Werkzeug reloader
try:
    import wymypy
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import wymypy.app
from wymypy.libs.flask import WyMyPyRequestHandler


logger = logging.getLogger(__name__)


def get_instances(mpd, bannend_plugins=[], plugin_configs={}):
    """ instantiate classes which inherits of me, return the list """
    instances = {}
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins")

    for plugin_file_name in os.listdir(base_dir):
        # filter out directories
        if not os.path.isfile(os.path.join(base_dir, plugin_file_name)): continue

        # filter out non py files
        if not plugin_file_name.endswith(".py"): continue

        # filter out special modules
        if plugin_file_name in ("__init__.py", ): continue

        # determine actual module name
        plugin_module_name = os.path.splitext(plugin_file_name)[0]

        # check for ban
        if plugin_module_name in bannend_plugins: continue

        # load it
        try:
            __import__("wymypy.plugins.%s" % plugin_module_name)
        except Exception, m:
            logger.exception("Plugin import error for [%(name)s]: %(error)s" % {'name': plugin_module_name, 'error': m})
            continue

        # lookup module
        plugin_module = sys.modules["wymypy.plugins.%s" % plugin_module_name]

        # lookup class
        if not hasattr(plugin_module, plugin_module_name.capitalize()): continue
        plugin_class = getattr(plugin_module, plugin_module_name.capitalize())

        # make sure its the right one
        if not inspect.isclass(plugin_class):
            continue

        logger.info(" - load plugin: %s" % plugin_module_name.capitalize())
        try:
            instances[plugin_module_name] = plugin_class(mpd, plugin_configs.get(plugin_module_name, {}))
            instances[plugin_module_name].name = plugin_module_name
        except Exception, m:
            logger.exception("Plugin instantiation error for %s: %s" % (plugin_module_name, m))
    return instances


def main(config_file="/etc/wymypy/wymypy.ini"):
    # load configuration
    wymypy.app.config.read(config_file)
    plugin_configs = {}
    for section in wymypy.app.config.sections():
        if not section.startswith("plugin-"): continue
        plugin_configs[section[7:]] = dict([(option, wymypy.app.config.get(section, option)) for option in wymypy.app.config.options(section)])

    # mpd->stream is special as it implies plugins-player->has_stream
    plugin_configs['player']['has_stream'] = bool(wymypy.app.config.get('mpd', 'stream'))

    # configure logging
    if wymypy.app.config.has_option("general", "logging"):
        logging.basicConfig(filename=wymypy.app.config.get("general", "logging"), format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)
    else:
        logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)

    # connect to MPD
    wymypy.app.mpd.connect(wymypy.app.config.get("mpd", "host"), wymypy.app.config.getint("mpd", "port"))

    # discover plugins
    wymypy.app.plugins = get_instances(wymypy.app.mpd, wymypy.app.config.get("plugins", "banned").split(","), plugin_configs)

    # start server
    wymypy.app.app.run(host=wymypy.app.config.get("server", "interface"),
                       port=wymypy.app.config.getint("server", "port"),
                       debug=wymypy.app.config.getboolean("general", "debug"),
                       request_handler=WyMyPyRequestHandler)

if __name__ == "__main__":
    main(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../etc/wymypy/wymypy.ini"))
