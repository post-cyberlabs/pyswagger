from __future__ import absolute_import
import six
import json
from .comm import PrimJSONEncoder
from ..errs import ValidationError, SchemaError

class Model(dict):
    """ for complex type: models
    """

    # access dict like object
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

    # Static class parameter: encoding/decoding style
    __collection_format = 'json'

    def __init__(self):
        """ constructor
        """
        super(Model, self).__init__()

    def __str__(self):
        """
        :return: the converted string
        :rtype: str
        """

        if self.__collection_format == 'raw':
            return dict.__str__(self)
        elif self.__collection_format == 'json':
            return json.dumps(self, cls=PrimJSONEncoder)
        else:
            raise SchemaError('Unsupported collection format when converting to str: {0}'.format(self.__collection_format))

    def apply_with(self, obj, val, ctx):
        """ recursively apply Schema object

        :param obj.Model obj: model object to instruct how to create this model
        :param dict val: things used to construct this model
        """
        baseval = val
        if 'params' in ctx and not val:
            val = ctx['params']
        # If no value provided: either object is required or introspected
        # in both case we try to generate a valid object
        # (introspection will just skip required / value sanity check testing)
        if val == None and ctx['introspect']:
            val = {}
        elif val == None:
            val = {}
        for k, v in six.iteritems(val):
            if k in obj.properties:
                pobj = obj.properties.get(k)
                if pobj.readOnly == True and ctx['read'] == False:
                    raise Exception('read-only property is set in write context.')
                self[k] = ctx['factory'].produce(pobj, v, ctx=ctx)

            # TODO: patternProperties here
            # TODO: fix bug, everything would not go into additionalProperties, instead of recursive
            elif obj.additionalProperties == True:
                ctx['addp'] = True
            elif obj.additionalProperties not in (None, False):
                ctx['addp_schema'] = obj

        in_obj = set(six.iterkeys(obj.properties))
        in_self = set(six.iterkeys(self))

        # sets iterator are not reproducible
        # sort it will avoid issues if this fuction is used by iterators
        # or with the cycle guard
        other_prop = sorted(in_obj - in_self)
        for k in other_prop:
            p = obj.properties[k]
            if p.is_set("default"):
                self[k] = ctx['factory'].produce(p, p.default, ctx=ctx)
            elif ctx['introspect']:
                self[k] = ctx['factory'].produce(p, None, ctx=ctx)

        not_found = set(obj.required) - set(six.iterkeys(self))
        if len(not_found) and not ctx['introspect']:
            raise ValidationError('Model for {1} missing required key(s): {0}'.format(', '.join(not_found), ctx['name']))

        # remove assigned properties to avoid duplicated
        # primitive creation
        _val = {}
        for k in set(six.iterkeys(val)) - in_obj:
            _val[k] = val[k]

        if obj.discriminator:
            self[obj.discriminator] = ctx['name']

        return _val

    def cleanup(self, val, ctx):
        """
        """
        if ctx['addp'] == True:
            for k, v in six.iteritems(val):
                self[k] = v
            ctx['addp'] = False
        elif ctx['addp_schema'] != None:
            obj = ctx['addp_schema']
            #for k, v in six.iteritems(val):
            #    self[k] = ctx['factory'].produce(obj.additionalProperties, v)
            #ctx['addp_schema'] = None

        return {}

    def __eq__(self, other):
        """ equality operater,
        will skip checking when both value are None or no attribute.

        :param other: another model
        :type other: primitives.Model or dict
        """
        if other == None:
            return False

        for k, v in six.iteritems(self):
            if v != other.get(k, None):
                return False

        residual = set(other.keys()) - set(self.keys())
        for k in residual:
            if other[k] != None:
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)
