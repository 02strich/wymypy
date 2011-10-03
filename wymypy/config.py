# general configs
TAG_FORMAT      = "<b>%(artist)s</b> - %(title)s"
DEBUG		= True
BANNED_PLUGINS  = ['iradio']

# connection to MPD server
MPD_PORT = 6600
MPD_HOST = "localhost"

# web server config
SERVER_NAME   = 'localhost'
SERVER_IFACE  = '127.0.0.1'
SERVER_PORT   = 8000

# plugin specific configs
#---------------------------

# iradio plugin
COUCHDB_URL = ""

# pandora plugin
PANDORA_USERNAME = ""
PANDORA_PASSWORD = ""
PANDORA_PROXY    = ""