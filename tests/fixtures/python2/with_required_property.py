from __future__ import unicode_literals, print_function, division


class Test(object):
    def __init__(self, data=None):
        data = data or {}

        self.id = data["id"]
