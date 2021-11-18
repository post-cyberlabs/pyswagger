from __future__ import absolute_import
from ...errs import CycleDetectionError
from ...scan import Dispatcher
from ...spec.v3_0_0.parser import SchemaContext,ParameterContext
from ...spec.v3_0_0.objects import Schema,Parameter

class Resolve(object):
    """ pre-resolve '$ref' """

    class Disp(Dispatcher): pass

    @Disp.register([Schema])
    def _schema(self, _, obj, app):
        if obj.ref_obj:
            return

        r = getattr(obj, '$ref')
        if not r:
            return

        ro = app.resolve(r, SchemaContext)
        if not ro:
            raise ReferenceError('Unable to resolve: {0}'.format(r))
        if ro.__class__ != obj.__class__:
            raise TypeError('Referenced Type mismatch: {0}'.format(r))

        obj.update_field('ref_obj', ro)

    @Disp.register([Parameter])
    def _parameter(self, _, obj, app):
        if obj.ref_obj:
            return

        r = getattr(obj, '$ref')
        if not r:
            return

        ro = app.resolve(r, ParameterContext)
        if not ro:
            raise ReferenceError('Unable to resolve: {0}'.format(r))
        if ro.__class__ != obj.__class__:
            raise TypeError('Referenced Type mismatch: {0}'.format(r))

        obj.update_field('ref_obj', ro)
