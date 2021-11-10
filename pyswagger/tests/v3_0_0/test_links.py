from pyswagger import App, utils
from pyswagger.spec.v3_0_0 import objects
from ..utils import get_test_data_folder
from ...utils import final
import unittest
import os



class ResolveLinksTestCase(unittest.TestCase):
    """ test for $ref in links / parameters """

    @classmethod
    def setUpClass(kls):
        kls.app = App.create(get_test_data_folder(
            version='3.0.0',
            which="link-example.yaml"
        ))

    def test_links_schema(self):
        """ make sure $ref to Schema works """
        p = self.app.op['getUserByName'].responses['200'].links


        self.assertTrue('userRepositories' in p)
        param = p['userRepositories']
        print(param.__dict__)
        self.assertEqual(param.operationId , None)

        clinks = self.app.root.components.links
        print(clinks)
        self.assertTrue('UserRepositories' in clinks)
        clinkparam = clinks['UserRepositories'].parameters
        print(clinkparam)

        paramderef = utils.deref(param)
        print(param.__dict__)
        self.assertEqual(paramderef.operationId, "getRepositoriesByOwner")



    '''
        path = '#/components/schemas/NewPet'

        self.assertEqual(p.requestBody.content['application/json'].schema.type, None)
        self.assertEqual(utils.deref(p.requestBody.content['application/json'].schema).type, "object")


    def test_parameter(self):
        """ make sure $ref to Parameter works """
        p = self.app.s('/a').get

        self.assertEqual(len(p.parameters), 5)
        self.assertEqual(final(p.parameters[0]).name, 'p1_d')
        self.assertEqual(final(p.parameters[1]).name, 'p2_d')
        self.assertEqual(final(p.parameters[2]).name, 'p2')
        self.assertEqual(final(p.parameters[3]).name, 'p3_d')
        self.assertEqual(final(p.parameters[4]).name, 'p4_d')

    def test_response(self):
        """ make sure $ref to Response works """
        p = self.app.s('/a').get

        self.assertEqual(final(p.responses['default']).description, 'void, r1')

    def test_raises(self):
        """ make sure to raise for invalid input """
        self.assertRaises(ValueError, self.app.resolve, None)
        self.assertRaises(ValueError, self.app.resolve, '')


class DerefTestCase(unittest.TestCase):
    """ test for pyswagger.utils.deref """

    @classmethod
    def setUpClass(kls):
        kls.app = App._create_(get_test_data_folder(
            version='2.0',
            which=os.path.join('resolve', 'deref')
        ))

    def test_deref(self):
        od = utils.deref(self.app.resolve('#/definitions/s1'))

        self.assertEqual(id(od), id(self.app.resolve('#/definitions/s4')))
    '''
