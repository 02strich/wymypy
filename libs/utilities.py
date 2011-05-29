#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import UnitTest
import cgi

class InputProcessed(object):
    def read(self, *args):
        raise EOFError('The wsgi.input stream has already been consumed')
    readline = readlines = __iter__ = read

def get_post_form(environ):
    #~ assert is_post_request(environ)
    input = environ['wsgi.input']
    post_form = environ.get('wsgi.post_form')
    if (post_form is not None
        and post_form[0] is input):
        return post_form[2]
    # This must be done to avoid a bug in cgi.FieldStorage
    environ.setdefault('QUERY_STRING', '')
    fs = cgi.FieldStorage(fp=input,
                          environ=environ,
                          keep_blank_values=1)
    new_input = InputProcessed()
    post_form = (new_input, input, fs)
    environ['wsgi.post_form'] = post_form
    environ['wsgi.input'] = new_input
    return fs


@UnitTest.register
def testExplodePath():
    assert explodePath(None)==("","/")
    assert explodePath("") == ("","/")
    assert explodePath(" ") == ("","/")
    assert explodePath("/") == ("","/")
    assert explodePath("/kav") == ("","/kav")
    assert explodePath("kav") == ("","/kav")
    assert explodePath("/kav/") == ("kav","/")
    assert explodePath("/kav/yurg") == ("kav","/yurg")
    assert explodePath("/kav/yurg/") == ("kav","/yurg/")
    assert explodePath("kav/yurg/") == ("kav","/yurg/")
    assert explodePath("kav/yurg") == ("kav","/yurg")
    #~ assert UnitTest.exception("""explodePath(12)""") == AssertionError

def explodePath(path):
    """ return a tuple ( 1st_folder,following_path ) """
    if path==None: path="/"
    assert isinstance(path, basestring)
    path = path.strip()
    if path=="" or path[0]!="/": path="/"+path

    p=path.split("/")
    if path.count("/")==1:
        tup = ("",path)
    else:
        tup = (p[1] ,path[len("/"+p[1]):])
    return tup



if __name__ == "__main__":
    pass
