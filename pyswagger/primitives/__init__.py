from __future__ import absolute_import
from ..utils import deref, CycleGuard
from ..errs import ValidationError
from ._int import create_int, validate_int
from ._str import create_str, validate_str, validate_email_
from ._bool import create_bool
from ._byte import Byte
from ._time import Date, Datetime
from ._file import File
from ._float import create_float, validate_float
from ._array import Array
from ._model import Model
from ._uuid import UUID
from .comm import create_obj, _2nd_pass_obj
from .render import Renderer
from .codec import MimeCodec
import functools
import logging


logger = logging.getLogger(__name__)


# TODO: enum is suitable for all types, not only string


class Primitive(object):
    """ primitive factory
    """
    def __init__(self):
        from ._model import Model
        from ._array import Array

        self._map = {
            # int
            'integer': {
                'int32': (create_int, validate_int),
                'int64': (create_int, validate_int),

                None: (create_int, validate_int),
            },

            'number':{
                # float
                'float': (create_float, validate_float),
                'double': (create_float, validate_float),

                # integer
                'int32': (create_int, validate_int),
                'int64': (create_int, validate_int),

                None: (create_float, validate_float),
            },

            # str
            'string': {
                '': (create_str, validate_str),
                None: (create_str, validate_str),

                # TODO: add validation for email, uuid
                # TODO: add convertion of uuid from python's one
                'email': (create_str, validate_email_),
                'uuid': (functools.partial(create_obj, constructor=UUID), _2nd_pass_obj),
                'password': (create_str, validate_str),

                'byte': (functools.partial(create_obj, constructor=Byte), _2nd_pass_obj),
                'binary': (functools.partial(create_obj, constructor=Byte), _2nd_pass_obj),
                'date': (functools.partial(create_obj, constructor=Date), _2nd_pass_obj),
                'date-time': (functools.partial(create_obj, constructor=Datetime), _2nd_pass_obj),
            },

            # bool
            'boolean': {
                '': (create_bool, None),
                None: (create_bool, None),
            },

            # file
            'file': {
                '': (functools.partial(create_obj, constructor=File), _2nd_pass_obj),
                None: (functools.partial(create_obj, constructor=File), _2nd_pass_obj),
            },

            # array
            'array': {
                '': (functools.partial(create_obj, constructor=Array), _2nd_pass_obj),
                None: (functools.partial(create_obj, constructor=Array), _2nd_pass_obj),
            },

            # model / schema Object
            'object': {
                '': (functools.partial(create_obj, constructor=Model), _2nd_pass_obj),
                None: (functools.partial(create_obj, constructor=Model), _2nd_pass_obj),
            }
        }

    def get(self, _type, _format=None):
        r = self._map.get(_type, None)
        if r is None:
            return (None, None)
        if _format in r:
            return r.get(_format)
        return r.get(None)

    def register(self, _type, _format, creater, _2nd_pass=None):
        """ register a type/format handler when producing primitives

        example function to create a byte primitive:
        ```python
        def create_byte(obj, val, ctx):
            # val is the value used to create this primitive, for example, a
            # dict would be used to create a Model and list would be used to
            # create an Array

            # obj in the spec used to create primitives, they are
            # Header, Items, Schema, Parameter in Swagger 2.0.

            # ctx is parsing context when producing primitives. Some primitves needs
            # multiple passes to produce(ex. Model), when we need to keep some globals
            # between passes, we should place them in ctx
            return base64.urlsafe_b64encode(val)
        ```

        example function of 2nd pass:
        ```python
        def validate_int(obj, ret, val, ctx):
            # val, obj, ctx are the same as those in creater

            # ret is the object returned by creater

            # do some stuff
            check_min_max(obj, val)

            # remember to return val, the 'outer' val would be overwritten
            # by the one you return, if you didn't return, it would be None.
            return val
        ```

        pseudo function of 2nd pass in Model:
        ```python
        def gen_mode(obj, ret, val, ctx):
            # - go through obj.properties to create properties of this model, and add
            #   them to 'ret'.
            # - remove those values used in this pass in 'val'
            # - return val
        ```

        :param _type str: type in json-schema
        :param _format str: format in json-schema
        :param creater function: a function to create a primitive.
        :param _2nd_pass function: a function used in 2nd pass when producing primitive.
        """
        if _type not in self._map:
            self._map[_type] = {}
        self._map[_type][_format] = (creater, _2nd_pass)

    def produce(self, obj, val, ctx=None, name=None, required=None):
        ctx = {} if ctx == None else ctx
        """ factory function to create primitives

        :param pyswagger.spec.v2_0.objects.Schema obj: spec to construct primitives
        :param val: value to construct primitives

        :return: the created primitive
        """
        '''
        From OpenAPI (v3), Parameter object uses fixed fields:
            name
            in
            description
            required
            deprecated
            allowEmptyValue
        Rules for serialisation can be specified for simple scenarios using style and schema:
            style
            explode
            allowReserved
            schema (can be ref)
            example
            examples (can be ref)
        Rules for complex scenarios are specified using the content property
        schema and content are mutually exclusive
        '''
        obj = deref(obj)

        if 'name' not in ctx and hasattr(obj, 'name'):
            ctx['name'] = obj.name
        if 'guard' not in ctx:
            ctx['guard'] = CycleGuard()

        if 'addp_schema' not in ctx:
            # Schema Object of additionalProperties
            ctx['addp_schema'] = None
        if 'addp' not in ctx:
            # additionalProperties
            ctx['addp'] = False
        if '2nd_pass' not in ctx:
            # 2nd pass processing function
            ctx['2nd_pass'] = None
        if 'factory' not in ctx:
            # primitive factory
            ctx['factory'] = self
        if 'read' not in ctx:
            # default is in 'read' context
            ctx['read'] = True
        if 'introspect' not in ctx:
            # default is do not introspect, raise errors
            ctx['introspect'] = False

        # cycle guard
        ctx['guard'].update(obj)

        # Retrieve or act from schema object
        # For Swagger2, schema is either the schema property or a copy of the object itself
        # Note that this function is recursive
        # so we are maybe calling with the schema instead of the objects
        if name == None:
            name = getattr(obj, 'name', None)
        if hasattr(obj, "schema"):
            schema = deref(obj.schema)
            if name == None:
                name = ctx.get('name', None)
            if required == None:
                required = getattr(obj, 'required', None)
            return self.produce(schema, val, ctx=ctx, name=name, required=required)
        # Check default and required values for simple types
        val = obj.default if val == None else val
        if val == None:
            if required==True and not ctx['introspect']:
                raise ValueError('requires parameter: ' + name)

        ret = None

        if obj.properties:
            properties = deref(obj.properties)
        if obj.type:
            creater, _2nd = self.get(_type=obj.type, _format=obj.format)
            if not creater:
                raise ValueError('Can\'t resolve type from:(' + str(obj.type) + ', ' + str(obj.format) + ')')
            ret = creater(obj, val, ctx=ctx)
            if _2nd:
                val = _2nd(obj, ret, val, ctx=ctx)
                ctx['2nd_pass'] = _2nd
        elif len(properties) or obj.additionalProperties:
            ret = Model()
            val = ret.apply_with(obj, val, ctx=ctx)

        if isinstance(ret, (Date, Datetime, Byte, File)):
            # it's meanless to handle allOf for these types.
            return ret

        def _apply(o, r, v, c):
            if hasattr(ret, 'apply_with'):
                v = r.apply_with(o, v, c)
            else:
                _2nd = c['2nd_pass']
                if _2nd == None:
                    _, _2nd = self.get(_type=o.type, _format=o.format)
                if _2nd:
                    _2nd(o, r, v, c)
                    # update it back to context
                    c['2nd_pass'] = _2nd
            return v

        # handle allOf for Schema Object
        allOf = getattr(obj, 'allOf', None)
        if allOf:
            not_applied = []
            for a in allOf:
                a = deref(a)
                if not ret:
                    # try to find right type for this primitive.
                    ret = self.produce(a, val, ctx)
                else:
                    val = _apply(a, ret, val, ctx)

                if not ret:
                    # if we still can't determine the type,
                    # keep this Schema object for later use.
                    not_applied.append(a)
            if ret:
                for a in not_applied:
                    val = _apply(a, ret, val, ctx)

        # handle anyOf for Schema Object
        anyOf = getattr(obj, 'anyOf', None)
        if anyOf:
            not_applied = []
            excs = []
            for a in anyOf:
                a = deref(a)
                if not ret:
                    # try to find the right type for this primitive
                    try:
                        ret = self.produce(a, val, ctx)
                    except Exception as ex:
                        logger.warning("Cannot produce with value %s: %s" % (val, str(ex)))
                        excs.append(ex)
                else:
                    val = _apply(a, ret, val,ctx)

            # if we cannot find a matching object, its time to raise the exception
            if not ret and excs:
                # Raise the first one
                raise ValidationError("%s is not a valid value for any of the conditions: %s" % (val, " / ".join(list(map(lambda x: str(x), excs)))))

        if ret != None and hasattr(ret, 'cleanup'):
            val = ret.cleanup(val, ctx)

        return ret

    def is_primitive(self, _type):
        """ check if a given object refering to a primitive
        defined in spec.

        :param dict obj: object to be checked
        :return: True if this object is a primitive.
        """
        return _type in self._map.keys()


SwaggerPrimitive = Primitive
