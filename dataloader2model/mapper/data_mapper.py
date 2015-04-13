from collections import defaultdict
from contextlib import contextmanager
from copy import deepcopy
from functools import partial
import inspect
from itertools import chain
from django.db.models.loading import get_model


class BaseVisit(object):
    path_delimiter = '.'
    method_delimiter = '_'

    def __init__(self, tree):
        self.tree = tree

    def get_next_path_name(self, prev, name):
        return self.path_delimiter.join(filter(None, (prev, name)))

    def get_attr_name(self, path, name):
        return self.method_delimiter.join(self.get_next_path_name(path, name).split(self.path_delimiter)).lower()


class MethodBinder(BaseVisit):

    def _walk_tree(self, tree, obj, path=''):
        if isinstance(tree, list) and not tree:
            return
        elif isinstance(tree, list):
            for t in tree:
                self._walk_tree(t, obj, self.get_next_path_name(path, ''))

        if not isinstance(tree, dict):
            return

        for name, value in tree.items():

            if isinstance(value, (dict, list)):
                self._walk_tree(value, obj, self.get_next_path_name(path, name))
            else:
                attr_name = self.get_attr_name(path, name)
                self.bind_methods_to_obj(obj, attr_name, value)

    def bind_methods(self, obj):
        self._walk_tree(self.tree, obj)

    def get_model(self, app_name, model_name):
        return get_model(app_name, model_name)

    def get_model_attr(self, data):
        app_name, model_name, model_attr_name = data.split('.', 2)
        model = self.get_model(app_name, model_name)
        return model, model_attr_name

    def get_model_field(self, model, field_name):
        return model._meta.get_field(field_name)

    def is_model(self, value):
        return isinstance(value, basestring)

    def is_function(self, value):
        return callable(value)

    def bind_methods_to_obj(self, obj, attr_name, value):
        if not value:
            return

        if self.is_model(value):
            model, model_attr_name = self.get_model_attr(value)
            f = partial(self.model_method, model=model, attr=model_attr_name, obj=obj)
            setattr(obj, attr_name, f)
        if self.is_function(value):
            model, model_attr_name = self.get_model_attr(value.model_attr)
            f = partial(self.callable_method, model=model, attr=model_attr_name, obj=obj, call_func=value)
            setattr(obj, attr_name, f)

    def callable_method(self, val, model=None, attr=None, obj=None, call_func=None):
        if model is None or attr is None or call_func is None or obj is None:
            raise ValueError('Model or attribute or obj of call_func is not define.')
        obj.storage.store(model, attr, call_func(val))
        return model

    def model_method(self, val, model=None, attr=None, obj=None):
        if model is None or attr is None or obj is None:
            raise ValueError('Model or attribute is not define.')
        obj.storage.store(model, attr, val)
        return model


class Storage(object):

    def __init__(self):
        self.__objects = {}
        self.__collections = defaultdict(list)
        self.__fill_collection = False
        self.__collection_counter = 0
        self.__collection_base_obj = None

    @property
    def fill_collection(self):
        return self.__fill_collection

    @fill_collection.setter
    def fill_collection(self, value):
        if value != self.__fill_collection:
            self.__collection_counter = 0
            self.__collection_base_obj = None
        self.__fill_collection = value

    def store(self, model, attr, val):
        if self.fill_collection:
            self.store_collection_item(model, attr, val)
        elif model in self.__collections:
            for obj in self.__collections[model]:
                setattr(obj, attr, val)
        else:
            if model not in self.__objects:
                self.__objects[model] = model()
            setattr(self.__objects[model], attr, val)

    def store_collection_item(self, model, attr, val):
        if model in self.__objects:
            self.__collection_base_obj = self.__objects.pop(model)
            self.__collections[model] = []

        if self.__collection_counter < len(self.__collections[model]):
            obj = self.__collections[model][self.__collection_counter]
        elif self.__collection_base_obj:
            obj = deepcopy(self.__collection_base_obj)
        else:
            obj = model()
        setattr(obj, attr, val)
        self.__collections[model].insert(self.__collection_counter, obj)

    @contextmanager
    def fill_collection_context(self):
        self.fill_collection = True
        yield
        self.fill_collection = False

    @property
    def objects(self):
        return self.__objects

    @property
    def collections(self):
        return dict(self.__collections)

    def save(self, save_order=None):
        save_order = chain(self.objects.keys(), self.collections.keys()) if save_order is None else save_order[:]

        for model in save_order:
            objs = list(filter(None, [self.objects.get(model)])) or self.collections.get(model)
            for obj in objs:
                obj.save()


class SchemaVisit(BaseVisit):
    def __init__(self, tree):
        super(SchemaVisit, self).__init__(tree)
        self.storage = Storage()
        MethodBinder(tree).bind_methods(self)

    def _construct_model(self, tree, path=''):

        if isinstance(tree, list) and not tree:
            return
        elif isinstance(tree, list):
            self._construct_collection(tree, path)

        if not isinstance(tree, dict):
            return

        for name, value in tree.items():

            if isinstance(value, (dict, list)):
                self._construct_model(value, self.get_next_path_name(path, name))
            else:
                attr_name = self.get_attr_name(path, name)
                self.call_method(attr_name, value)

    def _construct_collection(self, collection, path):

        if self.storage.fill_collection:
            raise ValueError('Collection in collection is not supported.')

        with self.storage.fill_collection_context():
            for counter, collection_item in enumerate(collection):
                self.__collection_counter = counter
                if isinstance(collection_item, dict):
                    self._construct_model(collection_item, path)

    def call_method(self, attr_name, value):
        attr = getattr(self, attr_name, None)
        if attr is not None and (inspect.ismethod(attr) or callable(attr)):
            attr(value)

    def construct_model(self, data):
        self._construct_model(data)
