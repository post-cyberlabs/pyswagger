from pyswagger import App, io, primitives
from ..utils import get_test_data_folder, get_test_file
from ...spec.v3_0_0.objects import OpenApi
import unittest
import os
import yaml

class Load_3_0_0_SpecTestCase(unittest.TestCase):
    """ test loading open-api 3.0 spec
    """

    def test_api_with_examples(self):
        """ load api-with-examples.yaml
        """
        App.create(get_test_data_folder(
            version='3.0.0',
            which="api-with-examples.yaml"
        ))


    def test_petstore_expanded(self):
        """ load petstore-expanded.yaml
        """
        App.create(get_test_data_folder(
            version='3.0.0',
            which="petstore-expanded.yaml"
        ))

    def test_petstore(self):
        """ load pestore.yaml
        """
        App.create(get_test_data_folder(
            version='3.0.0',
            which="petstore.yaml"
        ))

    def test_uspto(self):
        """ load uspto.yaml
        """
        App.create(get_test_data_folder(
            version='3.0.0',
            which="uspto.yaml"
        ))

    def test_link_example_json(self):
        """ load link-example.json
        """
        App.create(get_test_data_folder(
            version='3.0.0',
            which="link-example.json"
        ))

    def test_link_example(self):
        """ load link-example.yaml
        """
        App.create(get_test_data_folder(
            version='3.0.0',
            which="link-example.yaml"
        ))
