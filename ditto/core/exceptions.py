from __future__ import absolute_import, division, print_function, unicode_literals

class DiTToError(Exception):
    """
    Base class exception for the DiTTo package.
    """

class DiTToNotImplementedError(DiTToError): pass

# ETH@20170703 - Deriving all DiTTo errors from a common base class lets users
# isolate problems emanating from our package. In case the functionality provided 
# by TypeError and AttributeError is needed, I left them as base classes as well. 
# If that is not needed, single inheritance would be cleaner.
class DiTToTypeError(DiTToError,TypeError):
    pass

class DiTToAttributeError(DiTToError,AttributeError):
    pass

class DiTToNameError(DiTToError,AttributeError):
	pass
