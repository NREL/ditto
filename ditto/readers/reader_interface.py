"""Specifies the methods a Reader must implement."""

import abc


class ReaderInterface(abc.ABC):
    """Interface that any DiTTo reader must implement."""

    @abc.abstractmethod
    def list_capacitors(self):
        """Return capacitors from the data set.

        Returns
        -------
        list
            list of DiTTo.models.Capacitor

        """

    @abc.abstractmethod
    def list_feeders(self):
        """Return feeders from the data set.

        Returns
        -------
        list
            list of DiTTo.models.Feeder_metadata

        """

    @abc.abstractmethod
    def list_lines(self):
        """Return lines from the data set.

        Returns
        -------
        list
            list of DiTTo.models.Line

        """

    @abc.abstractmethod
    def list_loads(self):
        """Return loads from the data set.

        Returns
        -------
        list
            list of DiTTo.models.Load

        """

    @abc.abstractmethod
    def list_meters(self):
        """Return meters from the data set.

        Returns
        -------
        list
            list of DiTTo.models.Meter

        """

    @abc.abstractmethod
    def list_nodes(self):
        """Return nodes from the data set.

        Returns
        -------
        list
            list of DiTTo.models.Node

        """

    @abc.abstractmethod
    def list_phase_capacitors(self):
        """Return phase capacitors from the data set.

        Returns
        -------
        list
            list of DiTTo.models.PhaseCapacitor

        """

    @abc.abstractmethod
    def list_phase_loads(self):
        """Return phase loads from the data set.

        Returns
        -------
        list
            list of DiTTo.models.PhaseLoad

        """

    @abc.abstractmethod
    def list_phase_reactors(self):
        """Return phase reactors from the data set.

        Returns
        -------
        list
            list of DiTTo.models.PhaseReactors

        """

    @abc.abstractmethod
    def list_phase_storage(self):
        """Return phase storage from the data set.

        Returns
        -------
        list
            list of DiTTo.models.PhaseStorage

        """

    @abc.abstractmethod
    def list_phase_winding(self):
        """Return phase windings from the data set.

        Returns
        -------
        list
            list of DiTTo.models.PhaseWinding

        """

    @abc.abstractmethod
    def list_photovoltaics(self):
        """Return photovoltaics from the data set.

        Returns
        -------
        list
            list of DiTTo.models.Photovoltaic

        """

    @abc.abstractmethod
    def list_power_sources(self):
        """Return power_sources from the data set.

        Returns
        -------
        list
            list of DiTTo.models.PowerSource

        """

    @abc.abstractmethod
    def list_reactors(self):
        """Return reactors from the data set.

        Returns
        -------
        list
            list of DiTTo.models.Reactor

        """

    @abc.abstractmethod
    def list_regulators(self):
        """Return regulators from the data set.

        Returns
        -------
        list
            list of DiTTo.models.Regulator

        """

    @abc.abstractmethod
    def list_storage(self):
        """Return storage from the data set.

        Returns
        -------
        list
            list of DiTTo.models.Storage

        """

    @abc.abstractmethod
    def list_transformers(self):
        """Return transformers from the data set.

        Returns
        -------
        list
            list of DiTTo.models.PowerTransformer

        """

    @abc.abstractmethod
    def list_windings(self):
        """Return windings from the data set.

        Returns
        -------
        list
            list of DiTTo.models.Winding

        """

    @abc.abstractmethod
    def list_wires(self):
        """Return wires from the data set.

        Returns
        -------
        list
            list of DiTTo.models.Wire

        """

    @abc.abstractmethod
    def read_dataset(self, path, model, **kwargs):
        """Read the data set specified by path.

        Parameters
        ----------
        path : str
            filename or directory
        model : ditto.store.Store

        """
