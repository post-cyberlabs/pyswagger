from pyswagger import App
from ..utils import get_test_data_folder
import unittest
import os


class ValidationTestCase(unittest.TestCase):
    """ test validation of 3.0 spec """

    def test_read_only_and_required(self):
        """ a property is both read-only and required """
        app = App.load(get_test_data_folder(
            version='3.0.0',
            which="api-with-examples.json"
        ))
        errs = app.validate(strict=False)
        self.maxDiff = None
        self.assertEqual(sorted(errs), [])
