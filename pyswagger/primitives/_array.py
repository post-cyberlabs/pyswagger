from __future__ import absolute_import
from ..errs import ValidationError, SchemaError
from ..utils import deref
import functools
import six
import json


class Array(list):
    """ for array type, or parameter when allowMultiple=True
    """

    def __init__(self):
        """ v: list or string_types
        """
        super(Array, self).__init__()
        self.__collection_format = 'raw'

    def apply_with(self, obj, val, ctx):
        """
        """
        if val == None:
            val = []
        self.__collection_format = getattr(obj, 'collectionFormat', 'raw')

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
                val = json.loads(val)
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
            items = deref(obj.items)
            if items:# and len(val):
                # If no value is provided and introspect, let generate at least one item
                if not len(val) and ctx['introspect']:
                    val = [None]
                self.extend(map(functools.partial(ctx['factory'].produce, obj.items, ctx=ctx), val))
                val = []

        # init array as list
        if obj.minItems and len(self) < obj.minItems:
            raise ValidationError('Array should be more than {0}, not {1}'.format(obj.minItems, len(self)))
        if obj.maxItems and len(self) > obj.maxItems:
            raise ValidationError('Array should be less than {0}, not {1}'.format(obj.maxItems, len(self)))

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
            return json.dumps(self)
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
