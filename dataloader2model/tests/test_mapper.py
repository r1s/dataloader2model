import os
from types import ModuleType
import unittest
from mapper.data_mapper import BaseVisit, Storage
from mapper.schema_loader import Schema


class TestSchema(unittest.TestCase):

    def test_loader(self):
        module_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
        full_path = os.path.join(module_path, '__init__.py')

        s = Schema(full_path)
        self.assertIsInstance(s.load(), ModuleType)

        full_path = os.path.join(module_path, 'init_blabla.py')
        s = Schema(full_path)
        self.assertRaises(ValueError, s.load)

        full_path = os.path.join(module_path, 'blablabla')
        with open(full_path, 'wt') as f:
            f.write('bla' * 10)

        s = Schema(full_path)
        self.assertRaises(ImportError, s.load)
        os.remove(full_path)


class TestBaseVisit(unittest.TestCase):

    def test_get_next_path_name(self):
        base_visit = BaseVisit({})
        self.assertEqual(base_visit.get_next_path_name('', 'name'), 'name')
        self.assertEqual(base_visit.get_next_path_name('', ''), '')
        need_path = base_visit.path_delimiter.join(('main', 'name'))
        self.assertEqual(base_visit.get_next_path_name('main', 'name'), need_path)
        base_visit.path_delimiter = '+'
        need_path = base_visit.path_delimiter.join(('main', 'name'))
        self.assertEqual(base_visit.get_next_path_name('main', 'name'), need_path)

    def test_get_attr_name(self):
        base_visit = BaseVisit({})
        self.assertEqual(base_visit.get_attr_name('', 'name'), 'name')
        self.assertEqual(base_visit.get_attr_name('', ''), '')

        need_method_name = base_visit.method_delimiter.join(('main', 'name', 'somename'))
        source_path = base_visit.path_delimiter.join(('main', 'name'))
        self.assertEqual(base_visit.get_attr_name(source_path, 'somename'), need_method_name)


class TestStorage(unittest.TestCase):

    def test_fill_collection_context(self):
        s = Storage()
        s.fill_collection = False
        with s.fill_collection_context():
            self.assertTrue(s.fill_collection)
        self.assertFalse(s.fill_collection)

    def test_fill_collection(self):
        s = Storage()
        self.assertFalse(s.fill_collection)

        s.fill_collection = True
        s._Storage__collection_counter = 10
        s._Storage__collection_base_obj = 'Test'
        s.fill_collection = False
        self.assertEqual(s._Storage__collection_counter, 0)
        self.assertEqual(s._Storage__collection_base_obj, None)

        s._Storage__collection_counter = 10
        s._Storage__collection_base_obj = 'Test'
        s.fill_collection = True
        self.assertEqual(s._Storage__collection_counter, 0)
        self.assertEqual(s._Storage__collection_base_obj, None)

    def test_store(self):
        class A(object):
            pass

        class B(object):
            pass

        s = Storage()
        s.store(A, 'test', 'test')
        self.assertEqual(list(s.objects.keys())[0], A)
        self.assertIsInstance(list(s.objects.values())[0], A)
        self.assertEqual(list(s.objects.values())[0].test, 'test')

        s.store(A, 'test1', 'test1')
        self.assertEqual(len(list(s.objects.keys())), 1)
        self.assertEqual(list(s.objects.values())[0].test1, 'test1')

        s.store(B, 'bla', 'blabla')
        self.assertEqual(len(list(s.objects.keys())), 2)
        self.assertEqual(len(list(s.collections.keys())), 0)

        s.fill_collection = True
        s.store(A, 'test2', 'test2')
        self.assertEqual(len(list(s.objects.keys())), 1)
        self.assertEqual(len(list(s.collections.keys())), 1)
        self.assertEqual(len(s.collections[A]), 1)
        self.assertEqual(s.collections[A][0].test2, 'test2')
        self.assertEqual(s.collections[A][0].test, 'test')

        s.__Storage__collection_counter = 1
        s.store(A, 'test3', 'test3')
        self.assertEqual(len(s.collections[A]), 2)
        s.fill_collection = False

        s.store(A, 'test4', 'test4')
        for o in s.collections[A]:
            self.assertEqual(o.test4, 'test4')

if __name__ == '__main__':
    unittest.main()