#!/usr/bin/python
# -*- coding: utf-8 -*-

class UnitTest:
    __tests=[]

    @classmethod
    def register(cls,method):
        cls.__tests.append( method )
        return method

    @classmethod
    def run(cls):
        print "Run UnitTest"
        for method in cls.__tests:
            print ":: UnitTest : %s( )" % method.__name__
            method()

    @staticmethod
    def exception(strfct):
        try:
            return eval(strfct)
        except Exception,m:
            return m.__class__




#~ if __name__=="__main__":
    #~ UnitTest.run()

    #~ p="/kav/clone/tip/"
    #~ while 1:
        #~ (fct,path) = explodePath(p)
        #~ print p,"---->",(fct,path)
        #~ if fct=="":
            #~ break;
        #~ else:
            #~ p=path


    #~ p="/kav/clone/tip"
    #~ while 1:
        #~ (fct,path) = explodePath(p)
        #~ print p,"---->",(fct,path)
        #~ if fct=="":
            #~ break;
        #~ else:
            #~ p=path


