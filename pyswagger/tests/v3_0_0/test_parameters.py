# -*- coding: utf-8 -*-

from pyswagger import App, io, primitives
import pyswagger.contrib.client.requests
from ..utils import get_test_data_folder
from ...errs import SchemaError
import unittest
import os
import six
import json

class GetParametersTestCase(unittest.TestCase):
    """ test Parameter Introspection """

    @classmethod
    def setUpClass(kls):
        kls.app = App.create(get_test_data_folder(
            version='3.0.0',
            which="uspto.yaml"
        ))

    def testGetParams(self):

        op = self.app.s('/{dataset}/{version}/records').post

        params = []
        for data in op.parameters_iter():
            params.append(data)

        self.assertTrue(('path', 'version', 'v1') in params)
        self.assertTrue(('path', 'dataset', 'oa_citations') in params)
        self.assertTrue(('application/x-www-form-urlencoded', 'criteria', 'string') in params)
        self.assertTrue(('application/x-www-form-urlencoded', 'rows', 100) in params)
        self.assertTrue(('application/x-www-form-urlencoded', 'start', 0) in params)
        self.assertEqual(len(params),5)
