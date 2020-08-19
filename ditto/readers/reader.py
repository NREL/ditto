
import os

from ditto.common import InvalidConfiguration
from ditto.readers.abstract_reader import AbstractReader

from ditto.readers.gridlabd2.reader import GridlabdReader


class DiTToReader(AbstractReader):
    """Converts a dataset to a DiTTo model."""

    def __init__(self, path):
        self._intf = self.reader_interface_factory(path)
        self._path = path

    def parse(self, store, **kwargs):
        self._intf.read_dataset(self._path, store, **kwargs)
        # TODO call all list_* methods to add ditto objects to the store

    @staticmethod
    def reader_interface_factory(path):
        """Create a reader interface for the appropriate simulation engine.

        Returns
        -------
        ReaderInterface

        Raises
        ------
        InvalidConfiguration
            Raised if there is no supported engine.

        """
        if os.path.isfile(path):
            ext = os.path.splitext(path)[1]
            if ext == ".glm":
                return GridlabdReader()

        raise InvalidConfiguration(f"unknown reader interface format: {path}")
