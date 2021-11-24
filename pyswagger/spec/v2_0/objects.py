from __future__ import absolute_import
from ..base import BaseObj, FieldMeta
from ...utils import final, deref
from ...io import Request as IORequest
from ...io import Response as IOResponse
from ...primitives import Array, Model
import six
import copy


class BaseObj_v2_0(BaseObj):
    __swagger_version__ = '2.0'


class XMLObject(six.with_metaclass(FieldMeta, BaseObj_v2_0)):
    """ XML Object
    """
    __swagger_fields__ = {
        'name': None,
        'namespace': None,
        'prefix': None,
        'attribute': None,
        'wrapped': None,
    }


class BaseSchema(BaseObj_v2_0):
    """ Base type for Items, Schema, Parameter, Header
    """

    __swagger_fields__ = {
        'type': None,
        'format': None,
        'items': None,
        'default': None,
        'maximum': None,
        'exclusiveMaximum': None,
        'minimum': None,
        'exclusiveMinimum': None,
        'maxLength': None,
        'minLength': None,
        'maxItems': None,
        'minItems': None,
        'multipleOf': None,
        'enum': None,
        'pattern': None,
        'uniqueItems': None,
    }


class Items(six.with_metaclass(FieldMeta, BaseSchema)):
    """ Items Object
    """

    __swagger_fields__ = {
        'collectionFormat': 'csv',
    }

    def _prim_(self, v, prim_factory, ctx=None):
        return prim_factory.produce(self, v, ctx)


class Schema(six.with_metaclass(FieldMeta, BaseSchema)):
    """ Schema Object
    """

    __swagger_fields__ = {
        '$ref': None,
        'maxProperties': None,
        'minProperties': None,
        'required': [],
        'allOf': [],
        'properties': {},
        'additionalProperties': True,
        'title': None,
        'description': None,
        'discriminator': None,
        'readOnly': None,
        'xml': None,
        'externalDocs': None,
        'example': None,
    }

    __internal_fields__ = {
        # pyswagger only
        'ref_obj': None,
        'final': None,
        'name': None,
    }

    def _prim_(self, v, prim_factory, ctx=None):
        return prim_factory.produce(self, v, ctx)


class Swagger(six.with_metaclass(FieldMeta, BaseObj_v2_0)):
    """ Swagger Object
    """

    __swagger_fields__ = {
        'swagger': None,
        'info': None,
        'host': None,
        'basePath': None,
        'schemes': [],
        'consumes': [],
        'produces': [],
        'paths': None,
        'definitions': None,
        'parameters': None,
        'responses': None,
        'securityDefinitions': None,
        'security': None,
        'tags': None,
        'externalDocs': None,
    }


class Contact(six.with_metaclass(FieldMeta, BaseObj_v2_0)):
    """ Contact Object
    """

    __swagger_fields__ = {
        'name': None,
        'url': None,
        'email': None,
    }


class License(six.with_metaclass(FieldMeta, BaseObj_v2_0)):
    """ License Object
    """

    __swagger_fields__ = {
        'name': None,
        'url': None,
    }


class Info(six.with_metaclass(FieldMeta, BaseObj_v2_0)):
    """ Info Object
    """

    __swagger_fields__ = {
        'version': None,
        'title': None,
        'description': None,
        'termsOfService': None,
        'contact': None,
        'license': None,
    }


class Parameter(six.with_metaclass(FieldMeta, BaseSchema)):
    """ Parameter Object
    """

    __swagger_fields__ = {
        # Reference Object
        '$ref': None,

        'name': None,
        'in': None,
        'required': None,

        # body parameter
        'schema': None,

        # other parameter
        'collectionFormat': 'csv',

        # for converter only
        'description': None,

        # TODO: not supported yet
        'allowEmptyValue': False,
    }

    __internal_fields__ = {
        'final': None,
    }

    def _prim_(self, v, prim_factory, ctx=None):
        i = getattr(self, 'in')
        return prim_factory.produce(self.schema, v, ctx) if i == 'body' else prim_factory.produce(self, v, ctx)


class Header(six.with_metaclass(FieldMeta, BaseSchema)):
    """ Header Object
    """

    __swagger_fields__ = {
        'collectionFormat': 'csv',
        'description': None,
    }

    def _prim_(self, v, prim_factory, ctx=None):
        return prim_factory.produce(self, v, ctx)


class Response(six.with_metaclass(FieldMeta, BaseObj_v2_0)):
    """ Response Object
    """

    __swagger_fields__ = {
        # Reference Object
        '$ref': None,

        'schema': None,
        'headers': {},

        'description': None,
        'examples': None,
    }

    __internal_fields__ = {
        'final': None,
    }


class Operation(six.with_metaclass(FieldMeta, BaseObj_v2_0)):
    """ Operation Object
    """

    __swagger_fields__ = {
        'tags': None,
        'operationId': None,
        'consumes': [],
        'produces': [],
        'schemes': [],
        'parameters': None,
        'responses': None,
        'deprecated': False,
        'security': None,
        'description': None,
        'summary': None,
        'externalDocs': None,
    }

    __internal_fields__ = {
        'url': None,
        'path': None,
        'cached_schemes': [],
        # http method filled by patch_obj
        'method': None,
    }

    def _parameters_iter(self, p, schema=None, name=None, parameters=None, introspect=False, required=None):
        # At this point we are loading provided
        # arguments based on the swagger description

        # do not handle default or requirements manually
        # as this should be handled by the Primitive generation class
        parameters = parameters or {}
        v = parameters.get(name, None)

        # transform using the prim factory associated
        # to the datatype when patching the object
        c = p._prim_(v, self._prim_factory, ctx=dict(read=False,name=name,params=parameters,introspect=introspect,required=required))

        # do not provide value for parameters that user didn't specify.
        if c == None and not introspect:
            return

        # check parameter location
        i = getattr(p, 'in', name)

        # if the data specification is a file
        if schema.type == 'file':
            yield('file',name,c)
        # if a model is used outside of a query (form data...) explode it into parameters
        elif isinstance(c, Model) and i not in ['query','body']:
            for name,item in c.items():
                yield(i,name,item)
        # If It is a GET / POST parameter
        elif i in ('query', 'formData'):
            if isinstance(c, Array):
                if schema.items.type == 'file':
                    yield('file',name,c)
                else:
                    for item in c.to_url():
                        yield(i,name,item)
            else:
                # formData will be converted to real data by marshaller
                yield(i,name,c)
        else:
            # formData will be converted to real data by marshaller
            yield(i,name,c)

    def parameters_iter(self, introspect=True):

        if self.parameters:
            parameters = deref(self.parameters)
            for p in parameters:
                p = deref(p)
                if getattr(p,'content',None):
                    content = deref(p.content)
                    for mediatype in content:
                        _content = deref(content[mediatype])
                        _schema = deref(_content.schema)
                        yield from self._parameters_iter(_content, _schema, p.name, introspect=introspect)
                else:
                    _schema = deref(p.schema)
                    yield from self._parameters_iter(p, _schema, p.name, introspect=introspect)

    def __call__(self, **k):
        # prepare parameter set
        params = dict(header=[], query=[], path=[], body=[], formData=[], file=[])
        names = []
        for p in deref(self.parameters):
            p = deref(p)
            if getattr(p,'content',None):
                content = deref(p.content)
                for mediatype in content:
                    _content = deref(content[mediatype])
                    _schema = deref(_content.schema)
                    for ptype,pname,pval in self._parameters_iter(_content, _schema, p.name, k):
                        if ptype not in params:
                            params[ptype] = []
                        if pname in k:
                            params[ptype].append((pname,pval))
                        names.append(pname)
            else:
                _schema = deref(p.schema)
                for ptype,pname,pval in self._parameters_iter(p, _schema, p.name, k):
                    if ptype not in params:
                        params[ptype] = []
                    if pname in k:
                        params[ptype].append((pname,pval))
                    names.append(pname)

        # check for unknown parameter
        unknown = set(six.iterkeys(k)) - set(names)
        if len(unknown) > 0:
            raise ValueError('Unknown parameters: {0}'.format(unknown))

        return \
        IORequest(op=self, params=params), IOResponse(self)


class PathItem(six.with_metaclass(FieldMeta, BaseObj_v2_0)):
    """ Path Item Object
    """

    __swagger_fields__ = {
        # Reference Object
        '$ref': None,

        'get': None,
        'put': None,
        'post': None,
        'delete': None,
        'options': None,
        'head': None,
        'patch': None,
        'parameters': [],
    }


class SecurityScheme(six.with_metaclass(FieldMeta, BaseObj_v2_0)):
    """ Security Scheme Object
    """

    __swagger_fields__ = {
        'type': None,
        'name': None,
        'in': None,
        'flow': None,
        'authorizationUrl': None,
        'tokenUrl': None,
        'scopes': None,
        'description': None,
    }


class Tag(six.with_metaclass(FieldMeta, BaseObj_v2_0)):
    """ Tag Object
    """

    __swagger_fields__ = {
        'name': None,
        'description': None,
        'externalDocs': None,
    }


class ExternalDocumentation(six.with_metaclass(FieldMeta, BaseObj_v2_0)):
    """ External Documentation Object
    """

    __swagger_fields__ = {
        'description': None,
        'url': None,
    }
