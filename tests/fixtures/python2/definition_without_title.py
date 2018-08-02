from __future__ import unicode_literals, print_function, division


class NoTitle(object):
    def __init__(self, data=None):
        data = data or {}

        self.x = data.get("x")
