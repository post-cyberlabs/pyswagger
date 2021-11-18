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
        for data in op.parameters_iter(introspect="value"):
            params.append(data)

        print(params)
        param = params[0]
        self.assertEqual(param[0],'path')
        self.assertEqual(param[1],'version')
        self.assertEqual(str(param[2]),'v1')
        param = params[1]
        self.assertEqual(param[1],'dataset')
        self.assertEqual(str(param[2]),'oa_citations')
        param = params[2]
        param = param[2]
        print(param['val'])
        self.assertEqual(list(param['val'].keys()),['criteria','rows','start'])
        self.assertEqual(param['val']['rows']['val'],100)

        self.assertEqual(len(params),3)
