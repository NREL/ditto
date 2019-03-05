import json


class Default_Values(object):
    """
    Class for parsing default values.
    """

    register_names = []

    def __init__(self, default_values_file, **kwargs):

        self.default_values_file = default_values_file

    def parse(self):

        with open(self.default_values_file) as f:
            values_dict = json.load(f)
        return values_dict
