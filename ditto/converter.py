import os
import datetime
import traceback
import json

import logging

from .store import Store

logger = logging.getLogger(__name__)


class Converter(object):
    """Converter class. Use to convert from one format to another through DiTTo.
    **Usage:**
    >>> converter=converter(feeder_list, from_format, to_format, verbose)
    :param feeder_list: List of feeder names
    :type feeder_list: List[str]
    :param from_format: Format to use as input
    :type from_format: str
    :param to_format: Format to use as ouput
    :type to_format: str
    :param verbose: Set verbose mode
    :type verbose: bool
    .. note::
        - Feeders should be located in ./inputs/{from_format}/{feeder_name}
        - Output will be located in ./outputs/{from_format}/{to_format}/{feeder_name}
        - Readers should be located in ditto/reader/{from_format}/read.py
        - Writers should be located in ditto/writers/{to_format}/write.py
    .. warnings::
        - Names should be consistent (be carefull with lower/upper case...)
        - Readers should have a parse method responsible for parsing and a consistent constructor
        - Writers should have a write method responsible for parsing and a consistent constructor
    Author: Nicolas Gensollen. October 2017
    """

    def __init__(
        self,
        registered_reader_class,
        registered_writer_class,
        input_path,
        output_path,
        verbose=True,
        **kwargs
    ):
        """Converter class CONSTRUCTOR."""

        self.reader_class = registered_reader_class

        if registered_writer_class is None:
            logger.warning("Writer class is set to None")

        self.writer_class = registered_writer_class

        # If the file provided is a JSON file, a configuration file is assumed
        self.config = {}
        if input_path.endswith(".json"):
            with open(input_path, "r") as fp:
                self.config = json.load(fp)

        self.feeder = input_path

        self.output_path = output_path

        # TODO: check if this is in the registered list
        self._from = registered_reader_class.format_name
        if registered_writer_class is not None:
            self._to = registered_writer_class.format_name
        else:
            self._to = None

        # Serialize the DiTTo model before writing it out.
        if (
            kwargs.get("json_path", None) is not None
            and kwargs.get("registered_json_writer_class", None) is not None
        ):
            self.jsonize = True
            self.json_path = kwargs["json_path"]
            self.json_writer_class = kwargs["registered_json_writer_class"]
        else:
            self.jsonize = False
            self.json_path = False
            self.json_writer_class = None

        if kwargs.get("default_values_json", None) is not None:
            self.default_values_json = kwargs["default_values_json"]
        else:
            self.default_values_json = None

        if kwargs.get("remove_opendss_default_values_flag", None) is True:
            self.remove_opendss_default_values_flag = True
        else:
            self.remove_opendss_default_values_flag = False

        if kwargs.get("synergi_warehouse_path", None) is not None:
            self.synergi_warehouse_path = kwargs["synergi_warehouse_path"]
        else:
            self.synergi_warehouse_path = None

        self.verbose = verbose

        self.m = Store()

        # Set time format for log files
        self.time_format = "%H_%M_%d_%m_%Y"

    def get_inputs(self, feeder):
        """Configure Inputs."""
        # If we have a valid config there is nothing to do
        if len(self.config) > 0:
            return self.config
        # Otherwise...
        # Inputs are different accross the format:
        #
        # OpenDSS
        #
        if self._from == "opendss":
            inputs = {
                "master_file": os.path.abspath(feeder),
                "buscoordinates_file": os.path.join(
                    os.path.dirname(feeder), "buscoord.dss"
                ),
            }

        # CYME
        #
        elif self._from == "cyme":
            inputs = {
                "data_folder_path": os.path.abspath(feeder),
                "network_filename": "network.txt",
                "equipment_filename": "equipment.txt",
                "load_filename": "loads.txt",
            }

        # GRIDLABD
        #
        elif self._from == "gridlabd":
            inputs = {"input_file": os.path.abspath(feeder)}

        # Demo Case
        #
        elif self._from == "demo":
            inputs = {"input_file": os.path.abspath(feeder)}

        # SYNERGI
        #
        elif self._from == "synergi":
            inputs = {
                "input_file": os.path.abspath(feeder),
                "warehouse": "warehouse.mdb",
            }

        # DEW
        # TODO....
        elif self._from == "dew":
            inputs = {
                "input_file_path": "./inputs/{format}/{feeder}/{feeder}.dew".format(
                    format=self._from, feeder=feeder
                ),
                "databasepath": "../readers/dew/DataBase/DataBase.xlsx",
            }

        else:
            raise NotImplementedError("Format {} not imlemented.".format(self._from))

        if self.default_values_json:
            inputs["default_values_file"] = self.default_values_json
        else:
            inputs["default_values_file"] = None

        if self.remove_opendss_default_values_flag is True:
            inputs["remove_opendss_default_values_flag"] = True
        else:
            inputs["remove_opendss_default_values_flag"] = False

        # Add log information
        # log_path='./logs/reader/{format}/{feeder}/'.format(format=self._from,feeder=feeder)

        # Add filename to the log path
        # log_path+='/log_{time}.log'.format(time=self.current_time_string)

        # inputs.update({'log_file':log_path})
        self.config.update(inputs)

        return self.config

    def build_path(self, path):
        """Take a path as input and check that all folders exists as in the path.
        If folders are missing, they are created.
        .. warning:: Expects a path in the form './folder1/folder2/folder3/
        """
        # First we need to get all the directories in the given path
        dirs = path.split("/")

        # Loop over the directories and check for existance
        for k, _dir in enumerate(dirs):
            if k != 0:
                _tmp = reduce(lambda x, y: x + "/" + y, dirs[:k])
                if not os.path.exists(_tmp):
                    os.makedirs(_tmp)

        # Test that path exists
        if not os.path.exists(path):
            raise ValueError("Unable to create path {path}".format(path=path))

    def get_output(self, output_dir):
        """Configure outputs."""

        # TODO: Should we give the user the possibility to add these in the config file??
        output_path = output_dir
        log_path = os.path.join(output_dir, "out.log")

        return {"output_path": output_path, "log_file": log_path}

    def configure_reader(self, inputs):
        """Configure the reader."""

        logger.debug("Using Reader {} with inputs {}".format(self.reader_class, inputs))
        self.reader = self.reader_class(**inputs)

    def configure_writer(self, outputs):
        """Configure the writer."""

        if self.writer_class is not None:
            logger.debug(
                "Using Writer {} with outputs {}".format(self.writer_class, outputs)
            )
            self.writer = self.writer_class(**outputs)
        else:
            logger.error("Cannot configure the writer because Writer class is None.")

    def convert(self):
        """Run the conversion: from_format--->DiTTo--->to_format on all the feeders in feeder_list."""

        # Get the time for the log files (all log files created during the same call to convert()
        # will have the same timestamp which makes it easier to analyse them later)
        self.current_time_string = datetime.datetime.now().strftime(self.time_format)

        inputs = self.get_inputs(self.feeder)
        self.configure_reader(inputs)

        output = self.get_output(self.output_path)

        self.configure_writer(output)

        self.reader.parse(self.m)

        if self.jsonize:
            self.json_writer = self.json_writer_class(output_path=self.json_path)
            self.json_writer.write(self.m)

        self.writer.write(self.m)
