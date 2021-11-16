# -*- coding: utf-8 -*-

from pyswagger import App, io, primitives
from ..utils import get_test_data_folder
import unittest
import os
import six
import json


class OpenAPITestCase(unittest.TestCase):
    """ test OpenAPI (v3) specific features """

    @classmethod
    def setUpClass(kls):
        kls.app = App.create(get_test_data_folder(
            version='3.0.0',
            which="uspto.yaml"
        ))

    def test_server(self):
        self.assertEqual(self.app.root.servers[0].url, "{scheme}://developer.uspto.gov/ds-api")
        self.assertTrue('scheme' in self.app.root.servers[0].variables)
        self.assertEqual(self.app.root.servers[0].variables['scheme'].default, "https")
        self.assertEqual(self.app.root.servers[0].variables['scheme'].enum, ["https","http"])

    def test_patched_operation_url(self):

        print(self.app.s('/').get.url.geturl())
        self.assertEqual(self.app.s('/').get.url.geturl(), "https://developer.uspto.gov/ds-api")

    def test_body_data(self):
        op = self.app.s('/{dataset}/{version}/records').post
        print(op,op.requestBody.__dict__)
        self.assertTrue('application/x-www-form-urlencoded' in op.requestBody.content)
        self.assertEqual(op.requestBody.content['application/x-www-form-urlencoded'].schema.type,'object')
        self.assertTrue('start' in op.requestBody.content['application/x-www-form-urlencoded'].schema.properties)
        self.assertEqual(op.requestBody.content['application/x-www-form-urlencoded'].schema.properties['start'].type,'integer')

class OpenAPITestCaseNoServerVariables(unittest.TestCase):
    """ test OpenAPI (v3) specific features """

    def test_setupclass(self):
        filepath = get_test_data_folder(
            version='3.0.0',
            which="uspto_servertest.yaml"
        )
        self.assertRaises(ValueError,App.create, url=filepath)

        app = App.create(filepath, server={'uri': "hello.com"})
        self.assertEqual(app.s('/').get.url.geturl(), "https://hello.com/ds-api")
