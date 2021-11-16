from __future__ import absolute_import
from ..base import (
    Context,
    ContainerType,
    BaseObj,
    NullContext
    )
from .objects import (
    Schema,
    OpenApi,
    Components,
    Info,
    Parameter,
    Header,
    Response,
    Operation,
    Encoding,
    Example,
    PathItem,
    SecurityScheme,
    Reference,
    Tag,
    ExternalDocumentation,
    Contact,
    License,
    MediaType,
    Link,
    Server,
    ServerVariable,
    RequestBody,
    XML_)


class ExternalDocumentationContext(Context):
    """ Context of External Document
    """

    __swagger_ref_object__ = ExternalDocumentation


class XMLObjectContext(Context):
    """ Context of XML Object
    """

    __swagger_ref_object__ = XML_


class SchemaContext(Context):
    """ Context of Schema Object
    """
    __swagger_ref_object__ = Schema


# self-reference
setattr(SchemaContext, '__swagger_child__', {
    # items here should refer to an Schema Object.
    # refer to https://github.com/swagger-api/swagger-spec/issues/165
    # for details
    'items': (None, SchemaContext),
    'properties': (ContainerType.dict_, SchemaContext),
    # solution for properties with 2 possible types
#    'additionalProperties': (None, AdditionalPropertiesContext),
    'allOf': (ContainerType.list_, SchemaContext),
    'anyOf': (ContainerType.list_, SchemaContext),
#    'xml': (None, XMLObjectContext),
#    'externalDocs': (None, ExternalDocumentationContext),
})



class AdditionalPropertiesContext(Context):
    """ Context of additionalProperties,
    """

    class _TmpObj(BaseObj):
        def merge(self, other, _):
            if isinstance(other, bool):
                return other

            ret = Schema(NullContext())
            return ret.merge(other, SchemaContext)

    @classmethod
    def is_produced(kls, obj):
        """
        """
        if isinstance(obj, bool):
            return True
        return SchemaContext.is_produced(obj)

    def produce(self):
        """
        """
        if self.is_produced(self._obj):
            return self._obj
        else:
            return AdditionalPropertiesContext._TmpObj(self)

    def parse(self, obj=None):
        """
        """
        if obj == None:
            self._obj = True
        elif isinstance(obj, bool):
            self._obj = obj
        else:
            tmp = {'t': {}}
            with SchemaContext(tmp, 't') as ctx:
                ctx.parse(obj)

            self._obj = tmp['t']


# self-reference
#setattr(SchemaContext, '__swagger_child__', {
#    # items here should refer to an Schema Object.
#    # refer to https://github.com/swagger-api/swagger-spec/issues/165
#    # for details
#    'items': (None, SchemaContext),
#    'properties': (ContainerType.dict_, SchemaContext),
#    # solution for properties with 2 possible types
#    'additionalProperties': (None, AdditionalPropertiesContext),
#    'allOf': (ContainerType.list_, SchemaContext),
#    'xml': (None, XMLObjectContext),
#    'externalDocs': (None, ExternalDocumentationContext),
#})

class HeaderContext(Context):
    """ Context of Header Object
    """

    __swagger_child__ = {
        'schema': (None, SchemaContext),
        # items here should refer to an Items Object.
        # refer to https://github.com/swagger-api/swagger-spec/issues/165
        # for details
    }

    __swagger_ref_object__ = Header

class EncodingContext(Context):
    __swagger_ref_object__ = Encoding

    __swagger_child__ = {
        'headers': (ContainerType.dict_, HeaderContext),
    }

class ExampleContext(Context):
    __swagger_ref_object__ = Example

class MediaTypeContext(Context):

    __swagger_ref_object__ = MediaType

    __swagger_child__ = {
        'schema': (None, SchemaContext),
        'encoding': (None, EncodingContext),
        'examples': (None, ExampleContext),
    }

#        'schema': dict(child_builder=SchemaOrReference),
#        'examples': dict(child_builder=ExampleOrReference),
#        'encoding': dict(child_builder=map_(Encoding)),

class ParameterContext(Context):
    """ Context of Parameter Object, along with
    Reference Object
    """

    __swagger_child__ = {
        'schema': (None, SchemaContext),
        'content': (ContainerType.dict_, MediaTypeContext),
        # items here should refer to an Items Object.
        # refer to https://github.com/swagger-api/swagger-spec/issues/165
        # for details
    }

    __swagger_ref_object__ = Parameter

class ServerVariableContext(Context):

    __swagger_ref_object__ = ServerVariable

class ServerContext(Context):

    __swagger_ref_object__ = Server

    __swagger_child__ = {
        'variables': (ContainerType.dict_, ServerVariableContext),
    }

class LinkContext(Context):

    __swagger_ref_object__ = Link

    __swagger_child__ = {
        'server': (None, ServerContext),
        # parameters in link context is a dict of strings
        #'parameters': (ContainerType.dict_, ParameterContext),
    }

#        'server': dict(child_builder=Server),
#        'parameters': dict(child_builder=map_(is_str)),
#    }

#    __internal_fields__ = {
#        'operation_ref': dict(key='operationRef', builder=rename),
#        'operation_id': dict(key='operationId', builder=rename),
#        'request_body': dict(key='requestBody', builder=rename),


class ResponseContext(Context):
    """ Context of Response Object
    """

    __swagger_child__ = {
        'schema': (None, SchemaContext),
        'headers': (ContainerType.dict_, HeaderContext),
        'content': (ContainerType.dict_, MediaTypeContext),
        'links': (ContainerType.dict_, LinkContext),
    }
    __swagger_ref_object__ = Response


class RequestBodyContext(Context):

    __swagger_ref_object__ = RequestBody
    __swagger_child__ = {
        'content': (ContainerType.dict_, MediaTypeContext),
    }


class OperationContext(Context):
    """ Context of Operation Object
    """

    __swagger_child__ = {
        'parameters': (ContainerType.list_, ParameterContext),
        'responses': (ContainerType.dict_, ResponseContext),
        'requestBody': (None, RequestBodyContext),
    }
    __swagger_ref_object__ = Operation


class PathItemContext(Context):
    """ Context of Path Item Object
    """

    __swagger_child__ = {
        'get': (None, OperationContext),
        'put': (None, OperationContext),
        'post': (None, OperationContext),
        'delete': (None, OperationContext),
        'options': (None, OperationContext),
        'head': (None, OperationContext),
        'patch': (None, OperationContext),
        'trace': (None, OperationContext),
        'parameters': (ContainerType.list_, ParameterContext),
    }
    __swagger_ref_object__ = PathItem


class SecuritySchemeContext(Context):
    """ Context of Security Schema Object
    """

    __swagger_ref_object__ = SecurityScheme



class TagContext(Context):
    """ Context of Tag Object
    """

    __swagger_ref_object__ = Tag
    __swagger_child__ = {
        'externalDocs': (None, ExternalDocumentationContext),
    }


class ContactContext(Context):
    """ Context of Contact Object
    """

    __swagger_ref_object__ = Contact


class LicenseContext(Context):
    """ Context of License Object
    """

    __swagger_ref_object__ = License


class InfoContext(Context):
    """ Context of Info Object
    """

    __swagger_ref_object__ = Info
#    __swagger_child__ = {
#        'contact': (None, ContactContext),
#        'license': (None, LicenseContext),
#    }

class ComponentsContext(Context):

    __swagger_ref_object__ = Components
    __swagger_child__ = {
        'schemas': (ContainerType.dict_, SchemaContext),
        'responses': (ContainerType.dict_, ResponseContext),
        'parameters': (ContainerType.dict_, ParameterContext),
#        'examples': dict(child_builder=map_(ExampleOrReference)),
#        'requestBodies': dict(child_builder=map_(RequestBodyOrReference)),
        'headers': (ContainerType.dict_, HeaderContext),
        'links': (ContainerType.dict_, LinkContext),
#        'securitySchemes': dict(child_builder=map_(SecuritySchemeOrReference)),
#        'links': dict(child_builder=map_(LinkOrReference)),
#        'callbacks': dict(child_builder=map_(CallbackOrReference)),
    }

#class ServersContext(Context):
#    __swagger_ref_object__ = Servers


class OpenApiContext(Context):
    """ Context of Swagger Object
    """
    __swagger_ref_object__ = OpenApi

    __swagger_child__ = {
        'info': (None, InfoContext),
        'servers': (ContainerType.list_, ServerContext),
        'paths': (ContainerType.dict_, PathItemContext),
        'components': (None, ComponentsContext),
        #'security': (ContainerType.list_, SecurityContext),
        'tags': (ContainerType.list_, TagContext),
        #'externalDocs': (None, ExternalDocumentationContext),
    }
