from __future__ import absolute_import
from ...scan import Dispatcher
from ...spec.v3_0_0.objects import (
    Schema,
    Parameter,
    Header,
    Response,
    Operation,
    PathItem,
    OpenApi,
    )
from ...spec.v3_0_0.parser import (
    SchemaContext,
    ParameterContext,
    HeaderContext,
    ResponseContext,
    OperationContext,
    PathItemContext,
    OpenApiContext,
    )


class AssignParent(object):
    """ parent assignment """

    class Disp(Dispatcher): pass

    @Disp.register([Schema])
    def _schema(self, path, obj, _):
        obj._assign_parent(SchemaContext)

    @Disp.register([Parameter])
    def _parameter(self, path, obj, _):
        obj._assign_parent(ParameterContext)

    @Disp.register([Header])
    def _header(self, path, obj, _):
        obj._assign_parent(HeaderContext)

    @Disp.register([Response])
    def _response(self, path, obj, _):
        obj._assign_parent(ResponseContext)

    @Disp.register([Operation])
    def _operation(self, path, obj, _):
        obj._assign_parent(OperationContext)

    @Disp.register([PathItem])
    def _path_item(self, path, obj, _):
        obj._assign_parent(PathItemContext)

    @Disp.register([OpenApi])
    def _swagger(self, path, obj, _):
        obj._assign_parent(OpenApiContext)
