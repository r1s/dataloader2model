import os
import imp


class Schema(object):

    def __init__(self, path_to_schema):
        self.path_to_schema = path_to_schema
        self.name = '.'.join(os.path.basename(self.path_to_schema).split('.')[:-1])

    def load(self):

        if not os.path.exists(self.path_to_schema):
            raise ValueError('Path to {path_to_schema} not found.'.format(path_to_schema=self.path_to_schema))

        find_module = imp.find_module(self.name, [os.path.dirname(self.path_to_schema)])
        imp_module = imp.load_module(self.path_to_schema, *find_module)

        return imp_module