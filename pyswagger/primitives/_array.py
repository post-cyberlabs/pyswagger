from __future__ import absolute_import
from ..errs import ValidationError, SchemaError
from ..utils import deref
from .comm import PrimJSONEncoder
import functools
import six
import json

class Array(list):
    """ for array type, or parameter when allowMultiple=True
    """
    # Static class parameter: encoding/decoding style
    __collection_format = 'json'

    def __init__(self):
        """ v: list or string_types
        """
        super(Array, self).__init__()

    def apply_with(self, obj, val, ctx):
        """
        """
        # If no value provided: either object is required or being introspected
        # in both case we try to generate a valid object
        # (introspection will just skip required / value sanity check testing)
        # (and eventually there will be an array size check if the parameter is required)
        if val == None and ctx['introspect']:
            # Introspecting: we will try to generate an array with one object
            # in order to discover its structure recursively
            val = [None]
        elif val == None:
            val = []

        self.__collection_format = getattr(obj, 'collectionFormat', None) or self.__collection_format
        if isinstance(val, six.string_types):
            if self.__collection_format == 'csv':
                val = val.split(',')
            elif self.__collection_format == 'ssv':
                val = val.split(' ')
            elif self.__collection_format == 'tsv':
                val = val.split('\t')
            elif self.__collection_format == 'pipes':
                val = val.split('|')
            elif self.__collection_format == 'json':
                val = json.loads(val)#,cls=PrimJSONEncoder)
            else:
                raise SchemaError("Unsupported collection format '{0}' when converting array: {1}".format(self.__collection_format, val))

        # remove duplication when uniqueItems == True
        if obj.uniqueItems:
            if isinstance(val, (list, dict)):
                seen = []
                for e in val:
                    if e in seen:
                        continue
                    seen.append(e)
                val = seen
            else:
                # assume the type is hashable
                val = set(val)

        if obj.items:
            self.extend(map(functools.partial(ctx['factory'].produce, obj.items, ctx=ctx), val))

        # init array as list
        if obj.minItems and len(self) < obj.minItems:
            raise ValidationError('Array for {0} should be more than {1}, not {2}'.format(obj.name, obj.minItems, len(self)))
        if obj.maxItems and len(self) > obj.maxItems:
            raise ValidationError('Array for {0} should be less than {1}, not {2}'.format(obj.name, obj.maxItems, len(self)))

        return val

    def __str__(self):
        """ array primitives should be for 'path', 'header', 'query'.
        Therefore, this kind of convertion is reasonable.

        :return: the converted string
        :rtype: str
        """
        def _conv(p):
            s = ''
            for v in self:
                s = ''.join([s, p if s else '', str(v)])
            return s

        if self.__collection_format == 'csv':
            return _conv(',')
        elif self.__collection_format == 'ssv':
            return _conv(' ')
        elif self.__collection_format == 'tsv':
            return _conv('\t')
        elif self.__collection_format == 'pipes':
            return _conv('|')
        elif self.__collection_format == 'raw':
            return list.__str__(self)
        elif self.__collection_format == 'json':
            return json.dumps(self, cls=PrimJSONEncoder)
        else:
            raise SchemaError('Unsupported collection format when converting to str: {0}'.format(self.__collection_format))

    def to_url(self):
        """ special function for handling 'multi',
        refer to Swagger 2.0, Parameter Object, collectionFormat
        """
        if self.__collection_format == 'multi':
            return [str(s) for s in self]
        else:
            return [str(self)]
