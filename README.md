# DiTTo

[![](https://travis-ci.org/NREL/ditto.svg?branch=master)](https://travis-ci.org/NREL/ditto)
[![](https://badges.gitter.im/NREL/ditto.png)](https://gitter.im/NREL/ditto)
[![](https://img.shields.io/badge/docs-ready-blue.svg)](https://nrel.github.io/ditto)
[![codecov](https://codecov.io/gh/NREL/ditto/branch/master/graph/badge.svg)](https://codecov.io/gh/NREL/ditto)

DiTTo is the _Distribution Transformation Tool_. It is an open source tool to convert and modify electrical distribution system models. The most common domain of electrical distribution systems is from substations to customers.

## How it Works
Flexible representations for power system components are defined in the ditto models defined [here](https://github.com/NREL/ditto/tree/master/ditto/models)
DiTTo implements a _many-to-one-to-many_ parsing framework which makes it modular and robust. The [reader modules](https://github.com/NREL/ditto/tree/master/ditto/readers) parse data files of distribution system format (e.g. OpenDSS) and create an object for each electrical component. These objects are stored in a [Store](https://github.com/NREL/ditto/blob/master/ditto/store.py) instance. The [writer modules](https://github.com/NREL/ditto/tree/master/ditto/writers) are then used to export the data stored in memory to a selected output distribution system format (e.g. Gridlab-D) which are written to disk.

Additional functionality can be found in the documentation [here](https://nrel.github.io/ditto).

## Quick Start

### Install DiTTo

```bash
pip install ditto.py
```
This will install the basic version of ditto with limited dependencies.
Because ditto supports conversion between many multiple formats, dependencies can be specified during installation
For example:

```bash
pip install "ditto.py[extras,opendss,gridlabd]"
```
will install the required dependencies to convert between opendss and gridlab-d

To install the full dependency list run:

```bash
pip install "ditto.py[all]"
```
which is the same as
```bash
pip install "ditto.py[extras,opendss,cyme,dew,ephasor,synergi,gridlabd]" # same as `pip install "ditto.py[all]"`
```

### Basic Usage

The most basic capability of DiTTo is the conversion of a distribution system from one format to another.
To convert a cyme model represented in ASCII format with network.txt, equipment.txt and load.txt files, the following python script can be run to perform the conversion

```python
from ditto.store import Store
from ditto.readers.cyme.read import Reader
from ditto.writers.opendss.write import Writer

store = Store()
reader = Reader(data_folder_path = '.', network_file='network.txt',equipment_file = 'equipment.txt', load_file = 'load.txt')
reader.parse(store)
writer = Writer(output_path='.')
writer.write(store)

```

The required input files for each reader format are defined in the folder of each reader

### Command Line Interface

Ditto can also be run as a command line tool to perform basic conversion.
The CLI accepts only one input file whatever the format. If we have a gridlabd model entirely stored in a file called model.glm we can use:

```bash
$ ditto-cli convert --from glm --input ./model.glm --to cyme
```

For formats like CYME where multiple input files are needed, a simple JSON configuration file is supplied:

```json
{
    "data_folder_path": ".",
    "network_filename": "network.txt",
    "equipment_filename": "equipment.txt",
    "load_filename": "load.txt"
}
```
A default configuration file is found each reader folder.
So to convert the cyme files described in the python program above, the following command would be used:

```bash
$ ditto-cli convert --from cyme --input ./config.json --to dss
```

Documentation on converting other formats can be found [here](https://nrel.github.io/ditto/cli-examples).

## Contributing
DiTTo is an open source project and contributions are welcome! Either for a simple typo, a bugfix, or a new parser you want to integrate, feel free to contribute.

To contribute to Ditto in 3 steps:
- Fork the repository (button in the upper right corner of the DiTTo GitHub page).
- Create a feature branch on your local fork and implement your modifications there.
- Once your work is ready to be shared, submit a Pull Request on the DiTTo GitHub page. See the official GitHub documentation on how to do that [here](https://help.github.com/articles/creating-a-pull-request-from-a-fork/)

## Getting Help

If you are having issues using DiTTo, feel free to open an Issue on GitHub [here](https://github.com/NREL/ditto/issues/new)

All contributions are welcome. For questions about collaboration please email [Tarek Elgindy](mailto:tarek.elgindy@nrel.gov)
