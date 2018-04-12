import logging


from ditto.readers.abstract_reader import AbstractReader
from ditto.store import Store
from ditto.models.node import Node
from ditto.models.line import Line

logger = logging.getLogger(__name__)

class Reader(AbstractReader):
    '''
        Demo_format -> DiTTo Reader class
        Author: Tarek Elgindy April 2018

        This file provides a sample reader for a very simple model format
        containing only lines and nodes in a .txt file.

        The Demo file contains two types of entries - nodes and lines:

        Node <node_name>
        Line <line_name> <from_node> <to_node>

        An example system is given below:
        ---
        Node n1
        Node n2
        Node n3
        Node n4
        Line l1 n1 n2
        Line l2 n2 n3
        Line l3 n2 n4
        ---

        No other attributes are specified for this model format.
        

    '''

    def __init__(self, **kwargs):
        '''
            CYME-->Demo class constructor
        '''
        # Call super
        super(Reader, self).__init__(**kwargs)

        # Setting the file names and path
        
        # Set the path to the demo data file
        # Default is current directory
        if 'data_folder_path' in kwargs:
            self.data_folder_path = kwargs['data_folder_path']
        else:
            self.data_folder_path ='.' 

        # Set the name of the input file
        # Default is demo.txt
        if 'filename' in kwargs:
            self.filename = kwargs['filename']
        else:
            self.filename ='demo.txt'



    def get_file_content(self):
        '''
            Opens the file specified by self.filename in the location self.data_folder_path
            The content is stored in self.content
        '''
        filename = os.path.join(self.data_folder_path,self.filename)
        try:
            with open(filename, 'r') as f:
                content_ = f.readlines()
        except:
            raise ValueError('Unable to open file {name}'.format(name=filename))

        self.content = iter(content_)

    def parse(self, model, **kwargs):
        '''
            Parse the Demo model into DiTTO
            :param model: DiTTo model
            :type model:DiTTo model
            :param verbose: Set the verbose mode. Optional Default = True
            :type verbose: bool
        '''

        if 'verbose' in kwargs and isinstance(kwargs['verbose'], bool):
            self.verbose=kwargs['verbose']
        else:
            self.verbose=False

        #Call parse method of abtract reader
        self.get_file_content()     
        super(Reader, self).parse(model, **kwargs)    

    def parse_nodes(self, model):
        for line in self.content:
            data = line.split()
            
            # Skip lines without the right format
            if len(data) < 2:
                if self.verbose:
                    logger.info('Skipping line {name}'.format(name=line)
                continue
                
            if len(data) == 2 and data[0].lower()=='node':
                node = Node(model)
                node.name = data[1]


    def parse_lines(self, model):
        for line in self.content:
            data = line.split()
            if len(data) < 2:
                if self.verbose:
                    logger.info('Skipping line {name}'.format(name=line)
                continue
            
            if len(data) == 4 and data[0].lower() == 'line':
                line = Line(model)
                line.name = data[1]
                line.from_element = data[2]
                line.to_element = data[3]
            

            
