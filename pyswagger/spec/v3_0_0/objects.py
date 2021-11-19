from __future__ import absolute_import
from ..base import BaseObj, FieldMeta
from ...utils import final, deref
from ...io import Request as IORequest
from ...io import Response as IOResponse
from ...primitives import Array, Model
import six


class BaseObj_v3_0_0(BaseObj):
    __swagger_version__ = '3.0.0'


class Reference(BaseObj_v3_0_0):
    __swagger_fields__ = {
        #'$ref': None,
    }

    __internal_fields__ = {
        #'normalized_ref': None,
        #'ref_obj': None,

        #'ref': dict(key='$ref', builder=rename)
    }

    __swagger_rename__ = {
        #'ref': dict(key='$ref', builder=rename)
    }


def if_not_ref_else(class_builder):
    def _f(spec, path, override):
        if '$ref' in spec:
            return Reference(spec, path=path, override=override)
        return class_builder(spec, path=path, override=override)
    _f.__name__ = 'if_not_ref_else_' + class_builder.__name__
    return _f

def if_not_bool_else(class_builder):
    def _f(spec, path, override):
        if isinstance(spec, bool):
            return spec
        return class_builder(spec, path=path, override=override)
    _f.__name__ = 'if_not_bool_else_' + class_builder.__name__
    return _f

def is_str(spec, path, override):
    if override:
        raise Exception('attemp to override "str" in {}'.format(path))
    if isinstance(spec, six.string_types):
        return spec
    raise Exception('should be a string, not {}, {}'.format(str(type(spec)), path))

def is_str_or_int(spec, path, override):
    if override:
        raise Exception('attemp to override "str" in {}'.format(path))
    if isinstance(spec, six.string_types + six.integer_types):
        return spec
    raise Exception('should be a string or int, not {}'.format(str(type(spec)), path))


class Contact(six.with_metaclass(FieldMeta, BaseObj_v3_0_0)):
    __swagger_fields__ = {
        'name': None,
        'url': None,
        'email': None,
    }


class License(six.with_metaclass(FieldMeta, BaseObj_v3_0_0)):
    __swagger_fields__ = {
        'name': None,
        'url': None,
    }


class Info(six.with_metaclass(FieldMeta, BaseObj_v3_0_0)):
    __swagger_fields__ = {
        'version': None,
        'title': None,
        'description': None,
        'termsOfService': None,
        'contact': None,
        'license': None
    }

#    __children__ = {
#        'contact': dict(child_builder=Contact),
#        'license': dict(child_builder=License),
#    }

#    __internal_fields__ = {
#        'terms_of_service': dict(key='termsOfService', builder=rename),
#    }


class ServerVariable(six.with_metaclass(FieldMeta, BaseObj_v3_0_0)):
    __swagger_fields__ = {
        'default': None,
        'description': None,
        'enum': [],
    }

#    __internal_fields__ = {
#        'enum_': dict(key='enum', builder=rename)
#    }


class Server(six.with_metaclass(FieldMeta, BaseObj_v3_0_0)):
    __swagger_fields__ = {
        'url': None,
        'description': None,
        'variables': None,
    }

#    __children__ = {
#        'variables': dict(child_builder=map_(ServerVariable)),
#    }


class Example(six.with_metaclass(FieldMeta, BaseObj_v3_0_0)):
    __swagger_fields__ = {
        'summary': None,
        'description': None,
        'value': None,
        'externalValue': None,
    }

#    __internal_fields__ = {
#        'external_value': dict(key='externalValue', builder=rename),
#    }

ExampleOrReference = if_not_ref_else(Example)


class XML_(six.with_metaclass(FieldMeta, BaseObj_v3_0_0)):
    __swagger_fields__ = {
        'name': None,
        'namespace': None,
        'prefix': None,
        'attribute': None,
        'wrapped': None,
    }


class ExternalDocumentation(six.with_metaclass(FieldMeta, BaseObj_v3_0_0)):
    __swagger_fields__ = {
        'description': None,
        'url': None,
    }


class Discriminator(six.with_metaclass(FieldMeta, BaseObj_v3_0_0)):
    __swagger_fields__ = {
        'propertyName': None,
    }

#    __children__ = {
#        'mapping': dict(child_builder=map_(is_str)),
#    }

#    __internal_fields__ = {
#        'property_name': dict(key='propertyName', builder=rename),
#    }


class Schema(six.with_metaclass(FieldMeta, BaseObj_v3_0_0)):
    __swagger_fields__ = {
        '$ref': None,

        'title': None,
        'multipleOf': None,
        'maximum': None,
        'exclusiveMaximum': None,
        'minimum': None,
        'exclusiveMinimum': None,
        'maxLength': None,
        'minLength': None,
        'pattern': None,
        'maxItems': None,
        'minItems': None,
        'uniqueItems': None,
        'maxProperties': None,
        'minProperties': None,
        'required': [],
        'enum': None,
        'type': None, # Can be an array
        'items': None, # Must by an object not an array)
        'properties': None, # Must be a schema object
        'additionalProperties': None, # Can be boolean or object
        'description': None,
        'format': None,
        'default': None,
        'nullable': None,
        'discriminator': None,
        'readOnly': None,
        'writeOnly': None,
        'xml': None, # Only on properties schema
        'externalDocs': None,
        'example': None,
        'deprecated': None,

        'allOf': [],
        'anyOf': [],
        #'one_of': dict(key='oneOf', builder=rename),
        #'any_of': dict(key='anyOf', builder=rename),
        #'not_': dict(key='not', builder=rename),
    }

    __internal_fields__ = {
        # pyswagger only
        'ref_obj': None,
        'final': None,
        'name': None,
    }

    def _prim_(self, v, prim_factory, ctx=None):
        return prim_factory.produce(self, v, ctx)

#    __children__ = {
#        'discriminator': dict(child_builder=Discriminator),
#        'xml': dict(child_builder=XML_),
#        'externalDocs':  dict(child_builder=ExternalDocumentation),
#    }

#    __internal_fields__ = {
#        'multiple_of': dict(key='multipleOf', builder=rename),
#        'exclusive_maximum': dict(key='exclusiveMaximum', builder=rename),
#        'exclusive_minimum': dict(key='exclusiveMinimum', builder=rename),
#        'max_length': dict(key='maxLength', builder=rename),
#        'min_length': dict(key='minLength', builder=rename),
#        'max_items': dict(key='maxItems', builder=rename),
#        'min_items': dict(key='minItems', builder=rename),
#        'unique_items': dict(key='uniqueItems', builder=rename),
#        'max_properties': dict(key='maxProperties', builder=rename),
#        'min_properties': dict(key='minProperties', builder=rename),
#        'enum_': dict(key='enum', builder=rename),
#        'type_': dict(key='type', builder=rename),
#        'format_': dict(key='format', builder=rename),
#        'read_only': dict(key='readOnly', builder=rename),
#        'write_only': dict(key='writeOnly', builder=rename),
#        'xml_': dict(key='xml', builder=rename),
#        'external_docs': dict(key='externalDocs', builder=rename),

#        'all_of': dict(key='allOf', builder=rename),
#        'one_of': dict(key='oneOf', builder=rename),
#        'any_of': dict(key='anyOf', builder=rename),
#        'not_': dict(key='not', builder=rename),
#        'additional_properties': dict(key='additionalProperties', builder=rename),
#    }

#SchemaOrReference = if_not_ref_else(Schema)
#BoolOrSchemaOrReference = if_not_bool_else(SchemaOrReference)

#Schema.attach_field('allOf', builder=child, child_builder=list_(SchemaOrReference))
#Schema.attach_field('oneOf', builder=child, child_builder=list_(SchemaOrReference))
#Schema.attach_field('anyOf', builder=child, child_builder=list_(SchemaOrReference))
#Schema.attach_field('not', builder=child, child_builder=SchemaOrReference)
#Schema.attach_field('items', builder=child, child_builder=SchemaOrReference)
#Schema.attach_field('properties', builder=child, child_builder=map_(SchemaOrReference))
#Schema.attach_field(
#    'additionalProperties',
#    builder=child,
#    child_builder=BoolOrSchemaOrReference,
#)


class Parameter(six.with_metaclass(FieldMeta, BaseObj_v3_0_0)):
    __swagger_fields__ = {
        # Reference Object
        '$ref': None,

        'name': None,
        'in': None,
        'description': None,
        'required': None,
        'deprecated': None,
        'allowEmptyValue': None,
        'style': None,
        'explode': None,
        'allowReserved': None,
        'example': None,
        'schema': None,
        'content': None,
    }

#    __children__ = {
#        'examples': dict(child_builder=map_(ExampleOrReference)),
#        'schema': dict(child_builder=SchemaOrReference),
#    }

#    __internal_fields__ = {
#        'in_': dict(key='in', builder=rename),
#        'allow_empty_value': dict(key='allowEmptyValue', builder=rename),
#        'allow_reserved': dict(key='allowReserved', builder=rename),
#    }
    __internal_fields__ = {
        # pyswagger only
        'ref_obj': None,
        'final': None,
    }

    def _prim_(self, v, prim_factory, ctx=None):
        i = getattr(self, 'in')
        return prim_factory.produce(self.schema, v, ctx) if i == 'body' else prim_factory.produce(self, v, ctx)

ParameterOrReference = if_not_ref_else(Parameter)


class Header(Parameter):

    # Name must not be specified in header directly (will be in the headers map)
    # In must not be specified (implicit for header)
    pass

HeaderOrReference = if_not_ref_else(Header)


class Encoding(six.with_metaclass(FieldMeta, BaseObj_v3_0_0)):
    __swagger_fields__ = {
        'contentType': None,
        'stype': None,
        'explode': None,
        'allowReserved': None,
        'headers': None,
    }

#    __children__ = {
#        'headers'c: dict(child_builder=map_(HeaderOrReference)),
#    }

#    __internal_fields__ = {
#        'content_type': dict(key='contentType', builder=rename),
#        'allow_reserved': dict(key='allowReserved', builder=rename),
#    }


class MediaType(six.with_metaclass(FieldMeta, BaseObj_v3_0_0)):
    __swagger_fields__ = {
        'schema': None,
        'examples': None,
        'encoding': None,
    }

    def _prim_(self, v, prim_factory, ctx=None):
        return prim_factory.produce(self.schema, v, ctx)

    __internal_fields__ = {
        'name': None,
        'content_type': None,
        'in': None,
    }
#    __children__ = {
#        'schema': dict(child_builder=SchemaOrReference),
#        'examples': dict(child_builder=ExampleOrReference),
#        'encoding': dict(child_builder=map_(Encoding)),
#    }


#Parameter.attach_field('content', builder=child, child_builder=map_(MediaType))


class RequestBody(six.with_metaclass(FieldMeta, BaseObj_v3_0_0)):
    __swagger_fields__ = {
        'description': None,
        'content': None,
        'required': None,
    }

#    __children__ = {
#        'content': dict(child_builder=map_(MediaType), required=True),
#    }

RequestBodyOrReference = if_not_ref_else(RequestBody)


class Link(six.with_metaclass(FieldMeta, BaseObj_v3_0_0)):
    __swagger_fields__ = {
        # Reference Object
        '$ref': None,

        'operationRef': None,
        'operationId': None,
        'requestBody': None,
        'description': None,
        'server': None,
        'parameters': None,
    }

#    __children__ = {
#        'server': dict(child_builder=Server),
#        'parameters': dict(child_builder=map_(is_str)),
#    }

#    __internal_fields__ = {
#        'operation_ref': dict(key='operationRef', builder=rename),
#        'operation_id': dict(key='operationId', builder=rename),
#        'request_body': dict(key='requestBody', builder=rename),
#    }

LinkOrReference = if_not_ref_else(Link)


class Response(six.with_metaclass(FieldMeta, BaseObj_v3_0_0)):
    __swagger_fields__ = {
        # Reference Object
        '$ref': None,

        'description': None,
        'content': None,
        'links': None,
        'headers': None,
        'schema': None,
    }

    __internal_fields__ = {
        # pyswagger only
        'ref_obj': None,
        'final': None,
    }


ResponseOrReference = if_not_ref_else(Response)


class OAuthFlow(six.with_metaclass(FieldMeta, BaseObj_v3_0_0)):
    __swagger_fields__ = {
        'authorizationUrl': None,
        'tokenUrl': None,
        'refreshUrl': None,
    }

#    __children__ = {
#        'scopes': dict(child_builder=map_(is_str), required=True),
#    }

#    __internal_fields__ = {
#        'authorization_url': dict(key='authorizationUrl', builder=rename),
#        'token_url': dict(key='tokenUrl', builder=rename),
#        'refresh_url': dict(key='refreshUrl', builder=rename),
#    }


class OAuthFlows(BaseObj_v3_0_0):
    pass
#    __children__ = {
#        'implicit': dict(child_builder=OAuthFlow),
#        'password': dict(child_builder=OAuthFlow),
#        'clientCredentials': dict(child_builder=OAuthFlow),
#        'authorizationCode': dict(child_builder=OAuthFlow),
#    }

#    __internal_fields__ = {
#        'client_credentials': dict(key='clientCredential', builder=rename),
#        'authorization_code': dict(key='authorizationCode', builder=rename),
#    }


class SecurityScheme(six.with_metaclass(FieldMeta, BaseObj_v3_0_0)):
    __swagger_fields__ = {
        'type': None,
        'description': None,
        'name': None,
        'in': None,
        'scheme': None,
        'bearerFormat': None,
        'openIdConnectUrl': None,
    }

#    __children__ = {
#        'flows': dict(child_builder=OAuthFlows),
#    }

#    __internal_fields__ = {
#        'type_': dict(key='type', builder=rename),
#        'in_': dict(key='in', builder=rename),
#        'bearer_format': dict(key='bearerFormat', builder=rename),
#        'openid_connect_url': dict(key='openIdConnectUrl', builder=rename),
#    }

SecuritySchemeOrReference = if_not_ref_else(SecurityScheme)


class Operation(six.with_metaclass(FieldMeta, BaseObj_v3_0_0)):
    __swagger_fields__ = {
        'summary': None,
        'description': None,
        'operationId': None,
        'deprecated': None,
        'tags': [],
        'parameters': [],
        'requestBody': None,
        'responses': None,
        'security': None,
        'servers': None,

        # Internal
        'consumes': [],
        'produces': [],
    }

#    __children__ = {
#        'externalDocs': dict(child_builder=ExternalDocumentation),
#        'tags': dict(child_builder=list_(is_str)),
#        'parameters': dict(child_builder=list_(ParameterOrReference)),
#        'requestBody': dict(child_builder=RequestBodyOrReference),
#        'responses': dict(child_builder=map_(ResponseOrReference)),
#        'security': dict(child_builder=list_(map_(list_(is_str)))),
#        'servers': dict(child_builder=list_(Server)),
#    }

#    __internal_fields__ = {
#        'final_obj': None,

#        'external_docs': dict(key='externalDocs', builder=rename),
#        'operation_id': dict(key='operationId', builder=rename),
#        'request_body': dict(key='requestBody', builder=rename),
#    }

    __internal_fields__ = {
        'url': None,
        'path': None,
        'cached_schemes': [],
        # http method filled by patch_obj
        'method': None,
    }

    def _parameters_iter(self, p, schema=None, name=None, parameters=None, introspect=False):
        # At this point we are loading provided
        # arguments based on the swagger description

        # do not handle default or requirements manually
        # as this should be handled by the Primitive generation class
        parameters = parameters or {}
        v = parameters.get(name, None)

        # transform using the prim factory associated
        # to the datatype when patching the object
        c = p._prim_(v, self._prim_factory, ctx=dict(read=False,name=name,params=parameters,introspect=introspect))

        # do not provide value for parameters that user didn't specify.
        if c == None and not introspect:
            return

        # check parameter location
        i = getattr(p, 'in', name)

        # if the data specification is a file
        if schema.type == 'file':
            yield('file',name,c)
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
            if p.content:
                content = deref(p.content)
                for mediatype in content:
                    _content = deref(content[mediatype])
                    _schema = deref(_content.schema)
                    yield from self._parameters_iter(_content, _schema, p.name, introspect=introspect)
            else:
                _schema = deref(p.schema)
                yield from self._parameters_iter(p, _schema, p.name, introspect=introspect)

        if self.requestBody:
            if self.requestBody.content:
                content = deref(self.requestBody.content)
                for mediatype in content:
                    p = deref(content[mediatype])
                    _schema = deref(p.schema)
                    yield from self._parameters_iter(p, _schema, mediatype, introspect=introspect)

    def __call__(self, **k):
        # prepare parameter set
        params = dict(header=[], query=[], path=[], body=[], formData=[], file=[])
        names = []
        for p in deref(self.parameters):
            p = deref(p)
            if p.content:
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


        if self.requestBody:
            if self.requestBody.content:
                content = deref(self.requestBody.content)
                for mediatype in content:
                    params[mediatype] = []
                    p = deref(content[mediatype])
                    _schema = deref(p.schema)
                    for ptype,pname,pval in self._parameters_iter(p, _schema, mediatype, k):
                        if ptype not in params:
                            params[ptype] = []
                        params[ptype].append((pname,pval))
                        names.append(pname)

        # check for unknown parameter
        unknown = set(six.iterkeys(k)) - set(names)
        if len(unknown) > 0:
            raise ValueError('Unknown parameters: {0}'.format(unknown))

        return \
        IORequest(op=self, params=params), IOResponse(self)

class PathItem(six.with_metaclass(FieldMeta, BaseObj_v3_0_0)):
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
        'trace': None,
        'parameters': [],
    }

    __internal_fields__ = {
        # pyswagger only
        'ref_obj': None,
        'final': None,
    }

#    __internal_fields__ = {
#        'normalized_ref': None,
#        'ref_obj': None,
#        'final_obj': None,

#        'ref': dict(key='$ref', builder=rename),
#    }

#    __children__ = {
#        'get': dict(child_builder=Operation),
#        'put': dict(child_builder=Operation),
#        'post': dict(child_builder=Operation),
#        'delete': dict(child_builder=Operation),
#        'options': dict(child_builder=Operation),
#        'head': dict(child_builder=Operation),
#        'patch': dict(child_builder=Operation),
#        'trace': dict(child_builder=Operation),
#        'servers': dict(child_builder=list_(Server)),
#        'parameters': dict(child_builder=list_(ParameterOrReference)),
#    }


class Callback(six.with_metaclass(FieldMeta, BaseObj_v3_0_0)):
    pass
#    __swagger_version__ = '3.0.0'


#CallbackOrReference = if_not_ref_else(Callback)
#Operation.attach_field('callbacks', builder=child, child_builder=map_(CallbackOrReference))


class Components(six.with_metaclass(FieldMeta, BaseObj_v3_0_0)):
    __swagger_fields__ = {
        'schemas': None,
        'responses': None,
        'parameters': None,
        'examples': None,
        'requestBodies': None,
        'headers': None,
        'securitySchemes': None,
        'links': None,
        'callbacks': None,
    }

#    __internal_fields__ = {
#        'request_bodies': dict(key='requestBodies', builder=rename),
#        'security_schemes': dict(key='securitySchemes', builder=rename),
#    }


class Tag(six.with_metaclass(FieldMeta, BaseObj_v3_0_0)):
    __swagger_fields__ = {
        'name': None,
        'description': None,
        'externalDocs': None,
    }

#    __children__ = {
#        'externalDocs': dict(child_builder=ExternalDocumentation),
#    }

#    __internal_fields__ = {
#        'external_docs': dict(key='externalDocs', builder=rename),
#    }


class OpenApi(six.with_metaclass(FieldMeta, BaseObj_v3_0_0)):
    __swagger_fields__ = {
        'openapi': None,
        'info': None,
        'servers': None,
        'paths': None,
        'components': None,
        'security': None,
        'tags': None,
        'externalDocs': None,

        # Internal
        'consumes': [],
        'produces': [],
    }

#    __internal_fields__ = {
#        'external_docs': dict(key='externalDocs', builder=rename),
#    }
