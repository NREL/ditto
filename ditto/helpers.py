from builtins import super, range, zip, round, map
from __future__ import absolute_import, division, print_function
def model_function(model_class, doc=''):
    def func(self, *args, **kwargs):

        m = model_class(model=self, *args, **kwargs)

        return m

    return func
