from __future__ import unicode_literals, print_function, division


class Nested(object):
    def __init__(self, data=None):
        data = data or {}

        self.x = data.get("x")


class Test(object):
    def __init__(self, data=None):
        data = data or {}

        self.nested = None if data.get("nested") is None else Nested(data.get("nested"))
