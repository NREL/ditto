# coding: utf8

from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

import json
import json_tricks

from ditto.models.position import Position
from ditto.models.base import Unicode
from ditto.models.wire import Wire
from ditto.models.winding import Winding
from ditto.models.phase_winding import PhaseWinding
from ditto.models.phase_load import PhaseLoad
from ditto.models.phase_capacitor import PhaseCapacitor


class Writer(object):
    '''DiTTo--->JSON Writer class

The writer produce a file with the following format:

    - objects are stored in a list [object_1,object_2,...,object_N]
    - Each object is a dictionary object_1={'klass':'PowerTransformer',
                                            'is_substationr':{'klass':'int',
                                                              'value':'1'
                                                             },
                                            (...)
                                            }
    - The special key 'klass' indicates the type of the object considered.
    - klass can be:
            - a DiTTo object type like 'PowerTransformer' or 'Winding'
            - a "standard" type like 'int', 'float', or 'str'
            - a list ('list')
            - a complex number: 1+2j will be {'klass':'complex', 'value':[1,2]}

.. note:: For nested objects, this format can become a bit complex. See example below

**Example:**

object_1={'klass':'PowerTransformer',
          'is_substation':{'klass':'int',
                           'value':'1'
                         },
          'windings':{'klass':'list',
                      'value':[{'klass':'Winding',
                                'rated_power':{'klass':'float',
                                               'value':'1000'
                                               }
                                'phase_windings':{'klass':'list',
                                                  'value':[{'klass':'PhaseWinding',
                                                            'phase':{'klass':'Unicode',
                                                                     'value':'C'
                                                                     },
                                                            (...)
                                                            },
                                                            (...)
                                                            ]
                                                }
                                (...)
                                },
                                (...)
                              ]
                      },
            }

.. TODO:: Better format?

Author: Nicolas Gensollen. January 2018.

'''
    register_names = ["json", "Json", "JSON"]
    
    def __init__(self, **kwargs):
        '''Class CONSTRUCTOR

'''
        if 'output_path' in kwargs:
            self.output_path = kwargs['output_path']
        else:
            self.output_path = './out.json'

    def write(self, model):
        '''Write a given DiTTo model to a JSON file.
The output file is configured in the constructor.

'''

        _model = []
        for obj in model.models:
            _klass = type(obj).__name__
            if _klass in [Winding, PhaseWinding, Wire, PhaseCapacitor, Position, PhaseLoad]:
                continue
            _model.append({})
            _model[-1]['klass'] = _klass

            try:
                _model[-1]['name'] = {'klass': 'str', 'value': obj.name}
            except:
                _model[-1]['name'] = {'klass': 'str', 'value': None}
                pass

            for key, value in obj._trait_values.items():
                if key in ['capacitance_matrix', 'impedance_matrix', 'reactances']:
                    _model[-1][key] = {'klass': 'list', 'value': []}
                    for v in value:
                        if isinstance(v, complex):
                            _model[-1][key]['value'].append({'klass': 'complex', 'value': [v.real, v.imag]})
                        elif isinstance(v, list):
                            _model[-1][key]['value'].append({'klass': 'list', 'value': []})
                            for vv in v:
                                if isinstance(vv, complex):
                                    _model[-1][key]['value'][-1]['value'].append({'klass': 'complex', 'value': [vv.real, vv.imag]})
                                else:
                                    _model[-1][key]['value'][-1]['value'].append({'klass': str(type(vv)).split("'")[1], 'value': vv})
                        else:
                            _model[-1][key]['value'].append({'klass': str(type(v)).split("'")[1], 'value': v})
                    continue
                if isinstance(value, list):
                    _model[-1][key] = {'klass': 'list', 'value': []}
                    for v in value:

                        if isinstance(v, complex):
                            _model[-1][key]['value'].append({'klass': 'complex', 'value': [v.real, v.imag]})

                        elif isinstance(v, Position):
                            _model[-1][key]['value'].append({'klass': 'Position'})
                            for kkk, vvv in v._trait_values.items():
                                _model[-1][key]['value'][-1][kkk] = {'klass': str(type(vvv)).split("'")[1], 'value': vvv}

                        elif isinstance(v, Unicode):
                            _model[-1][key]['value'].append({'klass': 'Unicode', 'value': v.default_value})

                        elif isinstance(v, Wire):
                            _model[-1][key]['value'].append({'klass': 'Wire'})
                            for kkk, vvv in v._trait_values.items():
                                _model[-1][key]['value'][-1][kkk] = {'klass': str(type(vvv)).split("'")[1], 'value': vvv}

                        elif isinstance(v, PhaseCapacitor):
                            _model[-1][key]['value'].append({'klass': 'PhaseCapacitor'})
                            for kkk, vvv in v._trait_values.items():
                                _model[-1][key]['value'][-1][kkk] = {'klass': str(type(vvv)).split("'")[1], 'value': vvv}

                        elif isinstance(v, Winding):
                            _model[-1][key]['value'].append({'klass': 'Winding'})
                            for kkk, vvv in v._trait_values.items():
                                if kkk != 'phase_windings':
                                    _model[-1][key]['value'][-1][kkk] = {'klass': str(type(vvv)).split("'")[1], 'value': vvv}
                            _model[-1][key]['value'][-1]['phase_windings'] = {'klass': 'list', 'value': []}
                            for phw in v.phase_windings:
                                _model[-1][key]['value'][-1]['phase_windings']['value'].append({'klass': 'PhaseWinding'})
                                for kkkk, vvvv in phw._trait_values.items():
                                    _model[-1][key]['value'][-1]['phase_windings']['value'][-1][kkkk] = {
                                        'klass': str(type(vvvv)).split("'")[1],
                                        'value': vvvv
                                    }

                        elif isinstance(v, PhaseLoad):
                            _model[-1][key]['value'].append({'klass': 'PhaseLoad'})
                            for kkk, vvv in v._trait_values.items():
                                _model[-1][key]['value'][-1][kkk] = {'klass': str(type(vvv)).split("'")[1], 'value': vvv}

                    continue

                if isinstance(value, complex):
                    _model[-1][key] = {'klass': 'complex', 'value': [value.real, value.imag]}
                    continue

                _model[-1][key] = {'klass': str(type(value)).split("'")[1], 'value': value}

        with open(self.output_path, 'w') as f:
            try:
                f.write(json.dumps(_model))
            except:
                f.write(json_tricks.dumps(_model,allow_nan=True))
