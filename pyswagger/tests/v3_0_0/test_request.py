# -*- coding: utf-8 -*-

from ... import App, io, primitives, Security
from ...primitives import Primitive
from ...contrib.client.requests import Client
from ..utils import get_test_data_folder
from ...errs import SchemaError,ValidationError
import unittest
import os
import six
import json

class RequestTestCase(unittest.TestCase):
    """ test Request """

    @classmethod
    def setUpClass(kls):
        kls.app = App.create(get_test_data_folder(
            version='3.0.0',
            which="petstore.yaml"
        ))

    def test_client_simple(self):
        auth = Security(self.app)
        c = Client(auth)
        req,resp = self.app.op['listPets']()
        req._patch()
        req.prepare()
        self.assertEqual(req.url,"http://petstore.swagger.io/v1/pets")
        self.assertEqual(req.method,"get")
        self.assertEqual(req.path,"/pets")
        self.assertEqual(c.prepare_schemes(req), [])

    def test_client_args(self):
        auth = Security(self.app)
        c = Client(auth)
        self.assertRaises(ValidationError, self.app.op['showPetById'])

    def test_client_opts(self):
        auth = Security(self.app)
        c = Client(auth)

        req,resp = self.app.op['showPetById'](petId=3)
        req._patch({'url_netloc':"1.1.1.1", 'url_scheme':"https"})

        self.assertEqual(req.url,"https://1.1.1.1/v1/pets/{petId}")
        self.assertEqual(req.method,"get")
        self.assertEqual(req.path,"/pets/{petId}")
        self.assertEqual(c.prepare_schemes(req), [])

        req._patch({'url_netloc':"1.1.1.1", 'url_scheme':"http"})
        self.assertEqual(req.url,"http://1.1.1.1/v1/pets/{petId}")

        #self.assertEqual(c.prepare_schemes(req), ['http'])
        req.prepare(scheme='https')
        self.assertEqual(req.url,"https://1.1.1.1/v1/pets/3")

    def test_scheme(self):
        """ make sure Request.scheme works """

        # when didn't assign preference, use the first one in schemes
        req, _ = self.app.s('/pets').get()
        req.prepare(scheme=['https', 'http'])
        self.assertTrue(req.url.startswith('http'))

        # when assigned with preference, use the preference
        req, _ = self.app.s('/pets').get()
        req.scheme = 'https'
        req.prepare(scheme=['http', 'https'])
        self.assertTrue(req.url.startswith('https'))

        # when assinged with preference, and not available in input, raise Exception
        req, _ = self.app.s('pets').get()
        req.scheme = 'wss'
        self.assertRaises(Exception, req.prepare, scheme=['http'])

        # failed with scheme is not a list or string
        req, _ = self.app.s('pets').get()
        self.assertRaises(ValueError, req.prepare, scheme=1)

        # Check if operation object has been patched properly
        req, _ = self.app.s('pets').get()
        self.assertEqual(req.method,"get")
        self.assertEqual(req.path,"/pets")
        self.assertEqual(type(req.url),str)
        self.assertEqual(req.url,"http://petstore.swagger.io/v1/pets")


class RequestDataTestCase(unittest.TestCase):
    """ test Request """

    @classmethod
    def setUpClass(kls):
        kls.app = App.create(get_test_data_folder(
            version='3.0.0',
            which="uspto.yaml"
        ))

    def testPostParams(self):

        # the query model should failed as we removed the default for the criteria variable (a post data item)

        # as there is only one content_type for the body, the query should fail as the body is empty
        self.assertRaises(ValidationError, self.app.op['perform-search'], version="1",dataset="animals")

        req,resp = self.app.op['perform-search'](version="1",dataset="animals",criteria="*")

        op = self.app.s('/{dataset}/{version}/records').post

        print(op.requestBody.content['application/x-www-form-urlencoded'].schema.__dict__)

        # Providing an invalid parameter raises an error
        self.assertRaises(ValidationError, op, version="1",dataset="animals",blah="bluh")

        print(req.__dict__)

        print('request.url: {0}'.format(req.url))
        print('request.header: {0}'.format(req.header))
        print('request.query: {0}'.format(req.query))
        print('request.file: {0}'.format(req.files))
        print('request.schemes: {0}'.format(req.schemes))
        print('request.body: {0}'.format(req.body))
        print('request.data: {0}'.format(req.data))
        req.prepare()

        #self.assertRaises(SchemaError, req.prepare)

        req.consume('application/x-www-form-urlencoded')
        req.prepare()

        print('request.url: {0}'.format(req.url))
        print('request.header: {0}'.format(req.header))
        print('request.query: {0}'.format(req.query))
        print('request.file: {0}'.format(req.files))
        print('request.schemes: {0}'.format(req.schemes))
        print('request.body: {0}'.format(req.body))
        print('request.data: {0}'.format(req.data))

        self.assertEqual(req.data,[('application/x-www-form-urlencoded', 'criteria=%2A&rows=100&start=0')])
