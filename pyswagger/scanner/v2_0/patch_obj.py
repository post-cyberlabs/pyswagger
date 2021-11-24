from __future__ import absolute_import
from ...scan import Dispatcher
from ...spec.v2_0.objects import PathItem, Operation, Schema, Swagger, Parameter
from ...spec.v2_0.parser import PathItemContext, SchemaContext
from ...utils import jp_split, scope_split, final
import six
import copy


class PatchObject(object):
    """
    - produces/consumes in Operation object should override those in Swagger object.
    - parameters in Operation object should override those in PathItem object.
    - fulfill Operation.method, which is a pyswagger-only field.
    """

    class Disp(Dispatcher): pass

    @Disp.register([Operation])
    def _operation(self, path, obj, app):
        """
        """
        if isinstance(app.root, Swagger):
            # produces/consumes
            obj.update_field('produces', app.root.produces if len(obj.produces) == 0 else obj.produces)
            obj.update_field('consumes', app.root.consumes if len(obj.consumes) == 0 else obj.consumes)

        # combine parameters from PathItem
        if obj._parent_:
            # Operation parameters ovverride PathItem parameters
            if obj.parameters:
                for p in obj._parent_.parameters:
                    p_final = final(p)
                    for pp in obj.parameters:
                        if p_final.name == final(pp).name:
                            break
                    else:
                        obj.parameters.append(p)
            else:
                obj.update_field('parameters', copy.copy(obj._parent_.parameters))

        # schemes
        obj.update_field('cached_schemes', app.schemes if len(obj.schemes) == 0 else obj.schemes)

        # primitive factory
        setattr(obj, '_prim_factory', app.prim_factory)

        # inherit service-wide security requirements
        if obj.security == None and isinstance(app.root, Swagger):
            obj.update_field('security', app.root.security)

        # mime_codec
        setattr(obj, '_mime_codec', app.mime_codec)

    @Disp.register([PathItem])
    def _path_item(self, path, obj, app):
        """
        """
        k = jp_split(path)[-1] # key to the dict containing PathItem(s)
        if isinstance(app.root, Swagger):
            host = app.root.host if app.root.host else six.moves.urllib.parse.urlparse(app.url)[1]
            host = host if len(host) > 0 else 'localhost'
            base_path = app.root.basePath or ''
            url = six.moves.urllib.parse.ParseResult(
                    '',                            # schema
                    host,                          # netloc
                    base_path,                     # path
                    '', '', ''                     # param, query, fragment
            )

        else:
            url = None
            base_path = None

        for n in six.iterkeys(PathItemContext.__swagger_child__):
            o = getattr(obj, n)
            if isinstance(o, Operation):
                o.update_field('method', n)
                o.update_field('url', url)
                o.update_field('path', k)

    @Disp.register([Schema])
    def _schema(self, path, obj, app):
        """ fulfill 'name' field for objects under
        '#/definitions' and with 'properties'
        """
        if path.startswith('#/definitions'):
            last_token = jp_split(path)[-1]
            if app.version == '1.2':
                obj.update_field('name', scope_split(last_token)[-1])
            else:
                obj.update_field('name', last_token)

    @Disp.register([Parameter])
    def _parameter(self, path, obj, app):
        if obj.schema == None:
            # Ensure compatibility with OpenAPI
            # consider current object as a schema
            newschema = Schema(SchemaContext(self,None))
            obj.update_field('schema', newschema)

            obj.schema.update_field('type',obj.type)
            obj.schema.update_field('format',obj.format)
            obj.schema.update_field('items',obj.items)
            obj.schema.update_field('default',obj.default)
            obj.schema.update_field('maximum',obj.maximum)
            obj.schema.update_field('exclusiveMaximum',obj.exclusiveMaximum)
            obj.schema.update_field('minimum',obj.minimum)
            obj.schema.update_field('exclusiveMinimum',obj.exclusiveMinimum)
            obj.schema.update_field('maxLength',obj.maxLength)
            obj.schema.update_field('minLength',obj.minLength)
            obj.schema.update_field('maxItems',obj.maxItems)
            obj.schema.update_field('minItems',obj.minItems)
            obj.schema.update_field('multipleOf',obj.multipleOf)
            obj.schema.update_field('enum',obj.enum)
            obj.schema.update_field('pattern',obj.pattern)
            obj.schema.update_field('uniqueItems',obj.uniqueItems)
