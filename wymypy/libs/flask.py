from werkzeug.serving import WSGIRequestHandler


class WyMyPyRequestHandler(WSGIRequestHandler):
    # make sure we send the minimum amount of packets, as Cisco IP phones
    # will only use the first packet of the response
    wbufsize = -1

def join_result(func):
    def call_and_join(*args, **kwargs):
        result = func(*args, **kwargs)
        return "".join(result)
