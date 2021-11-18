from __future__ import absolute_import
from .comm import min_max


def validate_int(obj, ret, val, ctx):
    if ctx.get('introspect',False) and val == None:
        return val
    min_max(obj, ret, False)
    min_max(obj, ret, True)

    return val

def create_int(obj, v, ctx=None):
    if v == None:
        return 0
    r = int(v)
    validate_int(obj, r, v, ctx)
    return r
