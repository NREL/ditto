from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import open

import sys
import os
import decimal
import datetime
from collections import OrderedDict, Iterable
import networkx as nx

import enum
from lxml import etree
from six import string_types

from ..compat import ModuleType
from ..utils import combine

from .base import DiTToBase, PropertyType


# Use dir_path to locate schema.ecore
dir_path = os.path.dirname(os.path.realpath(__file__))

# Read schema.ecore and create a root XML node
with open(os.path.join(dir_path, 'schema.ecore'), encoding='utf-8') as f:
    schema = f.read()

root = etree.XML(schema.encode('utf-8'))

ns = {
    'xsi': "http://www.w3.org/2001/XMLSchema-instance",
    'ecore': "http://www.eclipse.org/emf/2002/Ecore",
}

# Global modules and classes that can be populated by functions
modules = OrderedDict()
classes = OrderedDict()

attr_docstrings = OrderedDict(DiTToBase='')
refr_docstrings = OrderedDict(DiTToBase='')

# Mapping for class types
class_types = {
    'float': float,
    'java.lang.Object': object,
    'java.lang.String': str,
    'java.math.BigDecimal': decimal.Decimal,
    'java.math.BigInteger': int,
}

# Mapping for core data types
core_data_types = {
    'BigDecimal': decimal.Decimal,
    'Boolean': bool,
    'Date': datetime.date,
    'Float': float,
    'Int': int,
    'String': str
}


def create_cim15_package():
    '''Interface to creating cim15 python package'''

    modules = create_cim15_modules()
    classes = create_cim15_classes()

    populate_cim15_package()

    cim15 = sys.modules[s('cim15')] = modules[s('cim15')]

    for name, m in modules.items():
        if name == s('cim15'):
            continue
        else:
            sys.modules[name] = m

    return cim15, modules, classes


def create_cim15_modules():
    '''Create python cim15 modules'''
    modules[s('cim15')] = ModuleType(s('cim15'))

    for package in root.findall(".//eSubpackages", namespaces=ns):
        module_name = 'cim15.' + '.'.join([p.get('name') for p in package.xpath('ancestor::eSubpackages')] + [package.get('name')])
        modules[s(module_name)] = ModuleType(s(module_name))

    return modules


def create_cim15_classes():
    '''Create python cim15 classes'''

    create_edatatype_classes()
    create_eenum_classes()
    create_eclass_classes()

    return classes


def populate_cim15_package():
    '''Populate the modules and the classes'''

    populate_modules_with_modules()
    populate_modules_with_classes()


def populate_modules_with_classes():
    '''Populate the modules with the classes'''

    for class_name, klass in classes.items():
        setattr(modules[klass.__module__], class_name, klass)


def populate_modules_with_modules():
    '''Populate the modules with the modules'''

    for k, module in modules.items():
        if k == s('cim15'):
            continue
        else:
            module_name = k.split('.')[-1]
            parent_module_name = '.'.join(k.split('.')[:-1])
            setattr(modules[parent_module_name], module_name, module)


def create_edatatype_classes():
    '''Create edatatype python classes

    eDataType classes inherit from Python base classes and have no attributes
    '''

    for c in root.findall('.//eClassifiers[@xsi:type="ecore:EDataType"]', namespaces=ns):
        module_name = 'cim15.' + '.'.join([p.get('name') for p in c.xpath('ancestor::eSubpackages')])
        class_name = c.get('name')

        # instanceClassName must exist in class_types, if not this will raise a KeyError
        class_type = class_types[c.get('instanceClassName')]

        docstring = find_docstring(c)
        # docstring = '''Parent: {}\n'''.format(class_type.__name__) + docstring

        # Create class dynamically
        c = type(class_name, (class_type, ), dict(__doc__=docstring))
        c.__module__ = s(module_name)

        classes[class_name] = c

    return classes


def create_eenum_classes():
    '''Create eenum python classes

    eEnum classes inherit from Python enum class.

    See Python enum for more information
    '''

    for c in root.findall('.//eClassifiers[@xsi:type="ecore:EEnum"]', namespaces=ns):

        module_name = 'cim15.' + '.'.join([p.get('name') for p in c.xpath('ancestor::eSubpackages')])
        class_name = c.get('name')
        class_type = enum.Enum

        docstring = find_docstring(c)
        # docstring = '''Parent: {}\n'''.format(class_type.__name__) + docstring

        l_docstring = ''
        enums = dict()
        for l in c.xpath('./eLiterals'):
            n = l.get('name')
            v = int(l.get('value', 0))
            enums[n] = v
            l_docstring = l_docstring + '{}\n'.format(n)

        title = 'Parameters'
        docstring = docstring + '''

{title}
{dashes}

{l}
'''.format(l=l, title=title, dashes='-' * len(title))

        # Create class dynamically
        c = type(class_name, (class_type, ), dict(__doc__=docstring, **enums))
        c.__module__ = s(module_name)

        classes[class_name] = c

    return classes


def create_eclass_classes():
    '''Create eclass python classes

    eClass classes inherit from a base class called DiTToBase
    attributes and references of eClass classes are created using descriptors/properties
    '''
    c_nodes = {i.get('name'): i for i in root.findall('.//eClassifiers[@xsi:type="ecore:EClass"]', namespaces=ns)}

    for parent, class_name in get_hierarchical_order():
        # c = root.find('.//eClassifiers[@xsi:type="ecore:EClass"][@name="{}"]'.format(class_name), namespaces=ns)
        c = c_nodes[class_name]
        module_name = 'cim15.' + '.'.join([p.get('name') for p in c.xpath('ancestor::eSubpackages')])
        module_name = module_name.strip('.')
        class_name = c.get('name')
        class_type = find_class_from_string(c.get('eSuperTypes'))
        if class_type is None:
            class_type = DiTToBase

        docstring = find_docstring(c)
        # docstring = '''Parent: {}\n'''.format(class_type.__name__) + docstring

        attributes = generate_attributes(c)
        references = generate_references(c)

        attr_docstrings[class_name], refr_docstrings[class_name] = generate_attributes_references_docstring(attributes, references)
        docstring = docstring + generate_parameters_docstring(attr_docstrings[class_name], refr_docstrings[class_name])
        attr_docstring, refr_docstring = chain_docstrings(class_type, '', '')
        docstring = docstring + generate_parameters_docstring(attr_docstring, refr_docstring, 'Other Parameters')

        # Create class dynamically
        c = type(class_name, (class_type, ), dict(__doc__=docstring, **combine(attributes, references)))
        c.__module__ = s(module_name)

        classes[class_name] = c

    return classes


def generate_attributes(c):
    '''Create a dictionary mapping the attribute name to the corresponding AttributeDescriptor'''

    attributes = dict()
    for e in c.xpath('./eStructuralFeatures[@xsi:type="ecore:EAttribute"]', namespaces=ns):

        name = e.get('name')
        eType = e.get('eType')
        type_check = find_class_from_string(eType)
        info_text = find_docstring(e)

        attributes[name] = AttributeDescriptor(name, type_check, info_text=info_text)

    return attributes


def generate_references(c):
    '''Create a dictionary mapping the reference name to the corresponding ReferenceDescriptor'''

    references = dict()
    for e in c.xpath('./eStructuralFeatures[@xsi:type="ecore:EReference"]', namespaces=ns):

        name = e.get('name')
        eType = e.get('eType')
        eOpposite = e.get('eOpposite')
        lowerBound = e.get('lowerBound')
        upperBound = e.get('upperBound')
        type_check = find_class_from_string(eType, lazy=True)
        opposite = find_class_from_string(eOpposite, lazy=True)
        info_text = find_docstring(e)

        references[name] = ReferenceDescriptor(name, type_check, opposite, lowerBound, upperBound, info_text=info_text)

    return references


def find_class_from_string(eType, lazy=False):
    '''Helper function to find the class from a string'''
    # TODO: Return class always instead of returning string

    if eType is None:
        klass = None
    elif eType.split('#')[1].strip('//E') in core_data_types:
        eType = eType.split('#')[1].strip('//E')
        klass = core_data_types[eType]
    else:
        eType = eType.strip('#//').replace('/', '.')
        if lazy is True:
            klass = eType.split('.')[-1]
        else:
            klass = classes[eType.split('.')[-1]]
    return klass


class AttributeDescriptor(PropertyType):

    def __init__(self, name, type_check, info_text='', lowerBound='1'):

        self.name = name
        self.type_check = type_check
        self.info_text = info_text
        self.lower_bound = lowerBound
        self.__doc__ = info_text.replace('\r', '').replace('\n', ' ')

    def __get__(self, obj, objtype):

        # Make descriptor behave like a property on classes
        if obj is None:
            return self

        try:
            # No type check on getting attribute? TODO: Decide if necessary
            return getattr(obj, '_' + self.name)
        except AttributeError:
            return None

    def __set__(self, obj, val):

        if self.type_check is not None and not isinstance(val, self.type_check):
            if issubclass(self.type_check, datetime.date):
                val = datetime.datetime.strptime(val, '%Y-%m-%d')
            else:
                val = self.type_check(val)
        setattr(obj, '_' + self.name, val)

    def __delete__(self, obj):
        delattr(obj, '_' + self.name)


class ReferenceDescriptor(PropertyType):

    def __init__(self, name, type_check, opposite, lowerBound, upperBound, info_text=''):
        self.name = name
        self.type_check = None
        self._type_check_string = type_check
        self.opposite = opposite
        self.info_text = info_text
        self.lower_bound = lowerBound
        self.upper_bound = upperBound
        self.error_string = 'a tuple of instances' if self.upper_bound == '-1' else 'an instance'
        self.__doc__ = info_text.replace('\r', '').replace('\n', ' ')

    def __get__(self, obj, objtype):

        # Make descriptor behave like a property on classes
        if obj is None:
            return self

        # Ensure that self.type_check is set with a class instance
        self.get_type()

        val = self.get_internal(obj)  # -> tuple

        if self.upper_bound is None:
            if len(val) == 0:
                val = None
            else:
                assert len(val) == 1, "Expected length of {}.{} to be one but found value {} instead".format(obj, '_' + self.name, val)
                val = val[0]
        else:
            if len(val) == 0:
                val = tuple()

        if val is not None:
            self.checks(val)  # TODO: Remove?

        self.call_get_callback(obj, val)

        return val

    def __set__(self, obj, val):

        # Ensure that self.type_check is set with a class instance
        self.get_type()

        # Clean previous value in reference stored in obj._name if it existed
        self.clean_previous(obj)

        if self.upper_bound == '-1':
            # val should be a tuple, verify
            self.is_iterable(val)  # TODO: Remove?
            # Received many values
            # Check type of each value
            for v in val:
                self.is_correct_type(v)

            # Setting the internal value to a tuple
            self.set_internal(obj, tuple(v for v in val))

            # For every value received, set the opposite value as well
            for v in val:
                self.set_opposite(obj, v)
        else:
            # val should be a single value
            self.is_correct_type(val)
            # Set internal to a tuple
            self.set_internal(obj, (val, ))
            # set the opposite references
            self.set_opposite(obj, val)

        self.call_set_callback(obj, val)

    def __delete__(self, obj):
        # TODO: clean?
        self.clean_previous(obj)
        delattr(obj, '_' + self.name)
        self.call_del_callback(obj)

    def get_internal(self, obj):  # -> tuple
        '''Get value from object
        Gets obj._name which is always a tuple
        It is an empty tuple of the value is not initailized yet
        '''

        try:
            val = getattr(obj, '_' + self.name)
        except AttributeError:
            val = tuple()

        self.assert_isinstance_tuple(val)
        return val

    def set_internal(self, obj, val):
        ''' Set obj._name to val. val must be of typle tuple '''

        self.assert_isinstance_tuple(val)
        setattr(obj, '_' + self.name, val)

    def checks(self, val):
        '''Checks if val is of correct length and correct type'''
        if self.upper_bound is None:
            # Only single value
            self.is_correct_type(val)
            return val
        elif self.upper_bound == '-1':
            # Always return tuple / iterable
            # val is a tuple, verify that it is a tuple TODO: is this necessary?
            self.is_iterable(val)
            # Check for individual values
            for v in val:
                self.is_correct_type(v)
            return val

    def is_iterable(self, val):
        if not isinstance(val, Iterable) or isinstance(val, string_types):
            raise TypeError("{} should be a tuple but instead found {} of type {}".format(self.name, val, type(val)))
        return val

    def is_correct_type(self, val):
        if not isinstance(val, self.type_check):
            raise TypeError('{} should be {} of type {} but instead found value "{}" of type {}'.format(self.name, self.error_string, self.type_check.__name__, val, type(val)))
        return val

    def get_type(self):
        if self.type_check is None:
            self.type_check = classes[self._type_check_string]

    def clean_previous(self, obj):
        '''Clean previous value if it exists'''

        value = self.get_internal(obj)
        for val in value:
            # For every object in value, find the opposite attribute and remove obj from it

            # Check is opposite value exists
            if self.get_opposite(val, '_') == tuple():
                continue

            # opposite attribute may be multiple or single
            ub = self.get_opposite(val.__class__).upper_bound

            # if opposite attribute is multiple
            if ub == '-1':
                # Get tuple of all objects that are not this obj
                v = tuple(v for v in self.get_opposite(val, '_') if not (v is obj or v == tuple()))
                # Set that as the new attribute on the opposite side
                setattr(val, '_' + self.opposite, v)
            else:
                # Delete the opposite attribute
                delattr(val, '_' + self.opposite)

    def set_opposite(self, obj, val):
        '''Set val of the opposite of obj._name'''

        # Find previous_value
        previous_value = self.get_opposite(val, '_')

        # Find if opposite is multiple or a single value
        ub = self.get_opposite(val.__class__).upper_bound

        if ub == '-1':
            # if opposite is mulitple values
            # set opposite value to a tuple
            new_value = previous_value + (obj, )
            self.assert_isinstance_tuple(new_value)

            setattr(val, '_' + self.opposite, new_value)

        else:
            # else opposite is a singe value
            setattr(val, '_' + self.opposite, (obj, ))

    def get_opposite(self, val, underscore=''):
        try:
            return getattr(val, underscore + self.opposite)
        except AttributeError:
            # Unable to find reference {} on {}".format(self.opposite, val)
            return tuple()

    def assert_isinstance_tuple(self, val):
        assert isinstance(val, tuple), TypeError("{} must be of type tuple".format(val))

    def call_get_callback(self, obj, val):
        f = self.callback(obj, 'get')
        if f is not None:
            f(self.name, val)

    def call_set_callback(self, obj, val):
        f = self.callback(obj, 'set')
        if f is not None:
            f(self.name, val)

    def call_del_callback(self, obj):
        f = self.callback(obj, 'del')
        if f is not None:
            f(self.name, obj)

    def callback(self, obj, type):
        try:
            return getattr(obj, '_callback_{}'.format(type))
        except AttributeError:
            return None


def find_docstring(element):
    '''Find docstring given a xml root element'''

    # There are two elements with documentation. Picking the one that contains cim16
    elements = element.xpath('./eAnnotations[contains(@source, "cim16")]/details[@key="Documentation"]')
    if not len(elements) <= 1:
        raise SyntaxError('Found {} "details" elements but expected 0 or 1.')

    if elements:
        annotation = elements[0]
        docstring = annotation.get('value')
    else:
        docstring = ''

    return docstring


def get_hierarchical_order():
    G = nx.DiGraph()

    for c in root.findall('.//eClassifiers[@xsi:type="ecore:EClass"]', namespaces=ns):
        class_name = c.get('name').decode('utf-8')
        class_type = c.get('eSuperTypes')
        class_type = find_class_from_string(class_type, lazy=True)
        if class_type is None:
            class_type = 'object'
        G.add_edge(class_type, class_name)

    return nx.bfs_edges(G, 'object')


def generate_attributes_references_docstring(attributes, references):
    '''Generate docstring for parameters'''

    attr_docstring = ''
    refr_docstring = ''
    for n, p in attributes.items():
        type_check_name = p.type_check.__name__ if p.type_check is not None else 'object'
        d = p.__doc__
        d = d if d != '' else 'Undocumented attribute'
        attr_docstring = attr_docstring + '{} : {}\n    {}\n'.format(n, type_check_name, d)
    for n, p in references.items():
        type_check_name = p._type_check_string
        opposite = p.opposite
        d = p.__doc__
        d = d if d != '' else 'Undocumented reference'
        d = '{} [bound to {}.{}]'.format(d, type_check_name, opposite)
        refr_docstring = refr_docstring + '{} : {}\n    {}\n'.format(n, type_check_name, d)

    return attr_docstring, refr_docstring


def chain_docstrings(c, a, r):

    for klass in c.mro():
        if klass is DiTToBase:
            break
        a = a + attr_docstrings[klass.__name__]
        r = r + refr_docstrings[klass.__name__]

    return a, r


def generate_parameters_docstring(attr_docstring, refr_docstring, title='Parameters'):
    return '''

{title}
{dashes}

{a}
{r}
'''.format(a=attr_docstring, r=refr_docstring, title=title, dashes='-' * len(title))


def s(string):
    '''Wrapper function for easier formatting of string'''
    return 'ditto.core.{}'.format(string)
