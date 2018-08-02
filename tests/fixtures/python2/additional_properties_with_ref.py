from __future__ import unicode_literals, print_function, division


class Value(object):
    def __init__(self, data=None):
        data = data or {}

        self.v = data.get("v")


class Test(object):
    def __init__(self, data=None):
        data = data or {}

        self.x = {
            k: Value(v) for k, v in ({} if data.get("x") is None else data.get("x")).iteritems()
        }
