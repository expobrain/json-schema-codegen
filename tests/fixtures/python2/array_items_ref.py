from __future__ import unicode_literals, print_function, division


class MyType(object):
    def __init__(self, data=None):
        data = data or {}

        self.v = data.get("v")


class Test(object):
    def __init__(self, data=None):
        data = data or {}

        self.x = [MyType(v) for v in ([] if data.get("x") is None else data.get("x"))]
