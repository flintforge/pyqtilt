import threading
import sys

class A:
    """docstring for ClassName"""
    def __init__(_,arg):
        _.valuestr = "AAA"
        _.arg = arg

def mydecorator(function):
    def _mydecorator(*args, **kw):
        # do some stuff before the real
        # function gets called
        res = function(*args, **kw)
        # do some stuff after
        return res
    # returns the sub-function
    return _mydecorator

def mydecorator1(function):
    def _mydecorator(*args):
        # do some stuff before the real
        # function gets called
        res = function(*args)
        # do some stuff after
        return res
    # returns the sub-function
    return _mydecorator


class TestClass:
    """docstring for ClassName"""

    def __init__(_, arg='DefaultArgument'):
        # super(ClassName, _).__init__()
        _.empty = None
        _.arg = arg
        _.abool = True
        _.abool2 = False
        _.aninteger = 423
        _.afloat = 3.1415
        _.astring = "hello"
        _.A = A(_)
        _.method = _.doit1_withdecorator

        _.atuple = (1,2,3,4)
        _.atuple2 = ([9,10],1)
        _.anarray = [5,6,7,8]
        _.asubarray = [[5,6],[7,8]]
        print('hi, im the new testclass', arg)
        # todo : an np array...

    def doit3(_,arg1,arg2='default'):
        print('you called me !', arg1,arg2)

    def doit2(_,arg1,arg2):
        print('called!',arg1,arg2)
        return TestClass(arg1)

    @mydecorator1
    def doit1_withdecorator(_,arg1):
        print('present!',arg1)
        return arg1

    @staticmethod
    def didit_static(_):
        print('yeah, didit',_)

    @classmethod
    def didit_class(_):
        print('yeah, didit',_)

    def x(_):
        return TestClass()

    def run_inc(_) :
        _.aninteger += 0.1
        print(_.aninteger)
        _.timer = threading.Timer(1.0, _.run_inc)

    def stop(_):
        print(_.aninteger)
        _.timer.cancel()

    @classmethod
    def out(_):
        sys.exit(0)
