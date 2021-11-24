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
            which="refcycle.yaml"
        ))


    def test_body_data(self):
        op = self.app.s('/nf-instances').put
        for a,b,c in op.parameters_iter():
            print(a,b,c.__repr__())
        #print(op,op.requestBody.__dict__)
        #self.assertTrue('application/x-www-form-urlencoded' in op.requestBody.content)
        #self.assertEqual(op.requestBody.content['application/x-www-form-urlencoded'].schema.type,'object')
        #self.assertTrue('start' in op.requestBody.content['application/x-www-form-urlencoded'].schema.properties)
        #self.assertEqual(op.requestBody.content['application/x-www-form-urlencoded'].schema.properties['start'].type,'integer')
