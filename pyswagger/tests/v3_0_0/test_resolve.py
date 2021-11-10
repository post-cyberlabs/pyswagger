from pyswagger import App, utils
from pyswagger.spec.v3_0_0 import objects
from ..utils import get_test_data_folder
from ...utils import final
import unittest
import os


class ResolvePathItemTestCase(unittest.TestCase):
    """ test for PathItem $ref """

    @classmethod
    def setUpClass(kls):
        kls.app = App.create(get_test_data_folder(
            version='3.0.0',
            which="petstore-expanded.yaml"
        ))

    def test_path_item(self):
        """ make sure PathItem is correctly merged """
        self.assertEqual(utils.jp_compose('/pets', '#/paths'),"#/paths/~1pets")
        a = self.app.resolve(utils.jp_compose('/pets', '#/paths'))

        self.assertTrue(isinstance(a, objects.PathItem))
        self.assertEqual(a.get.operationId, 'findPets')
        self.assertEqual(a.post.description, 'Creates a new pet in the store. Duplicates are allowed')


class ResolveSimpleTestCase(unittest.TestCase):
    """ test for $ref other than PathItem """

    @classmethod
    def setUpClass(kls):
        kls.app = App.create(get_test_data_folder(
            version='3.0.0',
            which="petstore-expanded.yaml"
        ))

    def test_schema(self):
        """ make sure $ref to Schema works """
        p = self.app.s('/pets').post

        path = '#/components/schemas/NewPet'

        self.assertEqual(p.requestBody.content['application/json'].schema.type, None)
        self.assertEqual(utils.deref(p.requestBody.content['application/json'].schema).type, "object")

class ResolvePrepareAppTestCase(unittest.TestCase):
    """ test for $ref other than PathItem """

    @classmethod
    def setUpClass(kls):
        kls.app = App.create(get_test_data_folder(
            version='3.0.0',
            which="petstore-expanded.yaml"
        ))

    def test_schema(self):
        """ make sure $ref to Schema works """
        p = self.app.s('/pets').post

        path = '#/components/schemas/NewPet'

        self.assertEqual(p.requestBody.content['application/json'].schema.type, None)


class PathItemMergeTestCase(unittest.TestCase):
    """ test case for merging external path item """

    @classmethod
    def setUpClass(kls):
        kls.app = App.create(get_test_data_folder(
            version='3.0.0',
            which="root.yml"
        ))

    def test_merge_basic(self):
        """ one path item in root ref to an external path item
        """
        pi = self.app.s('test1', before_return=None)

        def _not_exist(o):
            self.assertEqual(o.delete, None)
            self.assertEqual(o.options, None)
            self.assertEqual(o.head, None)
            self.assertEqual(o.patch, None)
            self.assertEqual(o.trace, None)

        # check original object is not touch, or 'dump' would be wrong
        _not_exist(pi)
        self.assertNotEqual(pi.post, None)

        another = self.app.resolve('file:///partial_path_item_1.yml#/test1', PathItem, '3.0.0', before_return=None)
        self.assertNotEqual(another.get, None)
        self.assertNotEqual(another.put, None)

        final = pi.final_obj
        _not_exist(final)
        self.assertNotEqual(final.get, None)
        self.assertNotEqual(final.post, None)
        # children objects are shared
        self.assertEqual(id(pi.post), id(final.post))
        self.assertEqual(id(another.get), id(final.get))
        self.assertEqual(id(another.put), id(final.put))

    def test_merge_cascade(self):
        """ path item in root ref to an external path item with
        ref to yet another path item, too
        """
        pi = self.app.s('test2', before_return=None)

        def _not_exist(o):
            self.assertEqual(o.put, None)
            self.assertEqual(o.delete, None)
            self.assertEqual(o.options, None)
            self.assertEqual(o.head, None)
            self.assertEqual(o.patch, None)
            self.assertEqual(o.trace, None)

        _not_exist(pi)
        self.assertEqual(pi.get, None)
        self.assertEqual(pi.post, None)

        another_1 = self.app.resolve('file:///partial_path_item_1.yml#/test2', before_return=None)
        _not_exist(another_1)
        self.assertNotEqual(another_1.get, None)
        self.assertEqual(another_1.post, None)

        another_2 = self.app.resolve('file:///partial_path_item_2.yml#/test2', before_return=None)
        _not_exist(another_2)
        self.assertEqual(another_2.get, None)
        self.assertNotEqual(another_2.post, None)

        final = pi.final_obj
        _not_exist(final)
        self.assertNotEqual(final.get, None)
        self.assertNotEqual(final.post, None)
        self.assertEqual(id(final.get), id(another_1.get))
        self.assertEqual(id(final.post), id(another_2.post))

    def test_no_ref_should_not_have_final(self):
        """ path item object without $ref
        should not have 'final_obj' property
        """
        pi = self.app.resolve('file:///partial_path_item_2.yml#/test2', before_return=None)
        self.assertEqual(pi.final_obj, None)

    def test_path_item_parameters(self):
        """ make sure parameters in path-item are handled
        """
        test4 = self.app.s('test4')

        p = test4.parameters[0]
        self.assertTrue(isinstance(p, Reference))
        self.assertNotEqual(p.ref_obj, None)

        p = test4.parameters[1]
        self.assertTrue(isinstance(p, Reference))
        self.assertNotEqual(p.ref_obj, None)


class ResolveTestCase(unittest.TestCase):
    """ test cases related to 'resolving' stuffs
    """

    @classmethod
    def setUpClass(kls):
        kls.app = App.create(get_test_data_folder(
            version='3.0.0',
            which="root.yml"
        ))

    def test_normalized_ref(self):
        """ make sure all '$ref' are cached with a normalized one
        """
        resp = self.app.s('test1', before_return=None).post.responses['default']
        self.assertTrue(isinstance(resp, Reference))
        self.assertEqual(resp.normalized_ref, 'file:///root.yml#/components/responses/void')

    def test_resolve_schema(self):
        """ make sure 'Schema' is resolved and cached
        """
        s = self.app.resolve('#/components/schemas/partial_1', before_return=None)
        self.assertTrue(isinstance(s, Reference))
        self.assertEqual(s.normalized_ref, 'file:///partial_1.yml#/schemas/partial_1')
        self.assertTrue(isinstance(s.ref_obj, Schema))
        self.assertEqual(s.ref_obj.type_, 'string')

    def test_resolve_parameter(self):
        """ make sure 'Parameter' is resolved and cached
        """
        p = self.app.s('test3', before_return=None).get.parameters[0]
        self.assertEqual(p.normalized_ref, 'file:///root.yml#/components/parameters/test3.p1')
        self.assertTrue(isinstance(p.ref_obj, Reference))

        p = p.ref_obj
        self.assertEqual(p.normalized_ref, 'file:///partial_1.yml#/parameters/test3.p1')
        self.assertTrue(isinstance(p.ref_obj, Parameter))

        p = p.ref_obj
        self.assertEqual(p.in_, 'query')

        s = p.schema
        self.assertTrue(isinstance(s, Reference))
        self.assertEqual(s.normalized_ref, 'file:///partial_2.yml#/schemas/test3.p1.schema')

        s = s.ref_obj
        self.assertTrue(isinstance(s, Schema))
        self.assertEqual(s.type_, 'string')
        self.assertEqual(s.format_, 'password')

    def test_resolve_header(self):
        """ make sure 'Header' is resolved and cached
        """
        p = self.app.s('test3', before_return=None).delete.parameters[0]
        self.assertTrue(isinstance(p, Reference))
        self.assertEqual(p.normalized_ref, 'file:///root.yml#/components/headers/test3.header.1')

        p = p.ref_obj
        self.assertTrue(isinstance(p, Reference))
        self.assertEqual(p.normalized_ref, 'file:///partial_1.yml#/headers/test3.header.1')

        h = p.ref_obj
        self.assertTrue(isinstance(h, Header))
        self.assertEqual(h.in_, 'header')
        self.assertEqual(h.name, None)
        self.assertTrue(isinstance(h.schema, Reference))
        self.assertEqual(h.schema.normalized_ref, 'file:///partial_2.yml#/schemas/test3.header.1.schema')

        s = h.schema.ref_obj
        self.assertTrue(isinstance(s, Schema))
        self.assertEqual(s.type_, 'integer')
        self.assertEqual(s.format_, 'int32')

    def test_resolve_request_body(self):
        """ make sure 'RequestBody' is resolved and cached
        """
        b = self.app.s('test3', before_return=None).post.request_body
        self.assertTrue(isinstance(b, Reference))
        self.assertEqual(b.normalized_ref, 'file:///root.yml#/components/requestBodies/test3.body.1')

        b = b.ref_obj
        self.assertTrue(isinstance(b, Reference))
        self.assertEqual(b.normalized_ref, 'file:///partial_1.yml#/bodies/test3.body.1')

        b = b.ref_obj
        self.assertTrue(isinstance(b, RequestBody))
        self.assertTrue('application/json' in b.content)

        s = b.content['application/json'].schema
        self.assertTrue(isinstance(s, Reference))
        self.assertEqual(s.normalized_ref, 'file:///root.yml#/components/schemas/test3.body.1.schema.1')

        s = s.ref_obj
        self.assertTrue(isinstance(s, Reference))
        self.assertEqual(s.normalized_ref, 'file:///partial_2.yml#/schemas/test3.body.1.schema.1')

        s = s.ref_obj
        self.assertTrue(isinstance(s, Schema))
        self.assertEqual(s.type_, 'object')
        self.assertTrue('email' in s.properties)
        self.assertEqual(s.properties['email'].type_, 'string')
        self.assertTrue('password' in s.properties)
        self.assertEqual(s.properties['password'].type_, 'string')
        self.assertEqual(s.properties['password'].format_, 'password')

    def test_resolve_response(self):
        """ make sure 'Response' is resolved and cached
        """
        r = self.app.s('test3', before_return=None).get.responses['400']
        self.assertTrue(isinstance(r, Reference))
        self.assertEqual(r.normalized_ref, 'file:///root.yml#/components/responses/BadRequest')

        r = r.ref_obj
        self.assertTrue(isinstance(r, Reference))
        self.assertEqual(r.normalized_ref, 'file:///partial_1.yml#/responses/test3.get.response.400')

        r = r.ref_obj
        self.assertTrue(isinstance(r, Response))
        self.assertEqual(r.description, 'test description')
        self.assertTrue('test-x-device-id' in r.headers)
        self.assertTrue('some-link' in r.links)

        h = r.headers['test-x-device-id']
        self.assertTrue(isinstance(h, Reference))
        h = h.ref_obj
        self.assertTrue(isinstance(h, Header))
        self.assertEqual(h.schema.type_, 'string')

        lk = r.links['some-link']
        self.assertTrue(isinstance(lk, Reference))
        lk = lk.ref_obj
        self.assertTrue(isinstance(lk, Link))
        self.assertEqual(lk.operation_ref, 'file:///root.yml#/paths/~1test1/post')
        self.assertTrue('id_1' in lk.parameters)
        self.assertEqual(lk.parameters['id_1'], '$response.body#/id_1')

    def test_resolve_components_callback(self):
        """ make sure 'Callback' in components is resolved and cached
        """
        cb = self.app.resolve('#/components/callbacks/cb.1', before_return=None)
        self.assertTrue(isinstance(cb, Reference))
        self.assertEqual(cb.normalized_ref, 'file:///partial_1.yml#/callbacks/cb.1')

        cb = cb.ref_obj
        self.assertTrue(isinstance(cb, Callback))
        self.assertEqual(cb['/test-cb-1'].summary, 'some test path item for callback')

        pi = cb['/test-cb-1'].get
        self.assertEqual(pi.operation_id, 'cb.1.get')
        p = pi.parameters[0]
        self.assertEqual(p.name, 'cb.1.p.1')
        self.assertEqual(p.in_, 'query')
        self.assertEqual(p.schema.type_, 'string')

        r = pi.responses['default']
        self.assertTrue(isinstance(r, Reference))
        self.assertEqual(r.normalized_ref, 'file:///root.yml#/components/responses/void')

        r = r.ref_obj
        self.assertTrue(isinstance(r, Response))
        self.assertEqual(r.description, 'void response')

        # able to resolve PathItem under callback
        p = self.app.resolve('file:///partial_1.yml#/callbacks/cb.1/~1test-cb-1', before_return=None)
        self.assertTrue(isinstance(p, PathItem))

    def test_resolve_operation(self):
        """ make sure 'Operation' is resolved and cached
        """
