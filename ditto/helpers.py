
def model_function(model_class, doc=''):

    def func(self, *args, **kwargs):

        m = model_class(model=self, *args, **kwargs)

        return m

    return func
