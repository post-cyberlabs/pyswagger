from __future__ import absolute_import
from ...scan import Dispatcher
from ...spec.v3_0_0.objects import PathItem, Operation, Schema, OpenApi, Parameter
from ...spec.v3_0_0.parser import PathItemContext
from ...utils import jp_split, scope_split, final, deref
import six
import copy
import logging

logger = logging.getLogger(__name__)

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
        if isinstance(app.root, OpenApi):
            # produces/consumes
            obj.update_field('produces', app.root.produces if len(obj.produces) == 0 else obj.produces)
            obj.update_field('consumes', app.root.consumes if len(obj.consumes) == 0 else obj.consumes)

        # combine parameters from PathItem
        if obj._parent_:
            # Operation parameters override PathItem parameters
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
        #obj.update_field('cached_schemes', app.schemes if len(obj.schemes) == 0 else obj.schemes)

        # primitive factory
        setattr(obj, '_prim_factory', app.prim_factory)

        # inherit service-wide security requirements
        if obj.security == None and isinstance(app.root, OpenApi):
            obj.update_field('security', app.root.security)

        # mime_codec
        setattr(obj, '_mime_codec', app.mime_codec)

    @Disp.register([PathItem])
    def _path_item(self, path, obj, app):
        """
        """
        k = jp_split(path)[-1] # key to the dict containing PathItem(s)

        if isinstance(app.root, OpenApi):
            host = None
            if hasattr(app.root,'servers') and app.root.servers:
                for server in app.root.servers:
                    if server.url:
                        host = server.url
                        if server.variables:
                            vars = {}
                            for name, vardata in server.variables.items():
                                if name in app.server:
                                    vars[name] = app.server[name]
                                elif vardata.default:
                                    logger.warning("Using default value for server variable %s : %s" % (name, vardata.default))
                                    vars[name] = vardata.default
                                else:
                                    if vardata.enum:
                                        raise ValueError("Server variable %s is required (proposals:%s)" % (name,",".join(vardata.enum)))
                                    else:
                                        raise ValueError("Server variable %s is required" % name)
                            host = host.format(**vars)
            if not host:
                host = six.moves.urllib.parse.urlparse(app.url)[1]
            #host = host if len(host) > 0 else 'localhost'
            url = six.moves.urllib.parse.urlparse(host)
        else:
            url = None

        for n in six.iterkeys(PathItemContext.__swagger_child__):
            o = getattr(obj, n)
            if isinstance(o, Operation):
                # path
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

        # patch object name based on its parent name
        elif not obj.name and obj._parent_ and hasattr(obj._parent_,'name') and obj._parent_.name:
            obj.update_field('name', obj._parent_.name)

        # Patch names of schema properties
        if obj.properties:
            for key,val in obj.properties.items():
                if not val.name:
                    val.update_field('name', key)
