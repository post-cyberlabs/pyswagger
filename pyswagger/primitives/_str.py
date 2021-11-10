from __future__ import absolute_import
import six
from ..errs import ValidationError
from validate_email import validate_email


def validate_str(obj, ret, val, ctx):
    enum = None

    if obj.schema.enum and ret not in obj.schema.enum:
        raise ValidationError('{0} is not a valid enum for {1}'.format(ret, str(obj.schema.enum)))
    if obj.schema.maxLength and len(ret) > obj.schema.maxLength:
        raise ValidationError('[{0}] is longer than {1} characters'.format(ret, str(obj.schema.maxLength)))
    if obj.schema.minLength and len(ret) < obj.schema.minLength:
        raise ValidationError('[{0}] is shorter than {1} characters'.format(ret, str(obj.schema.minLength)))

    # TODO: handle pattern
    return val

def create_str(obj, v, ctx=None):
    if isinstance(v, six.string_types):
        r = v
    else:
        r = str(v)
    validate_str(obj, r, v, ctx)
    return r

def validate_email_(obj, ret, val, ctx):
    if not validate_email(ret):
        raise ValidationError('{0} is not a valid email for {1}'.format(ret, obj))

    return val
