from __future__ import absolute_import


def create_bool(_, v, ctx=None):
    if v == None:
        return None
    return bool(v)
