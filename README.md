# DiTTo

## What is DiTTo?

DiTTo stands for _Distribution Transformation Tool_ and aims at providing an open source framework to convert various distribution systems modeling formats.
DiTTo implements a _many-to-one-to-many_ parsing framework which makes it modular and robust.
The main idea is that DiTTo has a core representation of what a distribution system is.
Readers and writers are then implemented to perform the translation from a given format to the core representation, or the other way around.

## Requirements

DiTTo requires >=Python2.7.
Additional Python dependencies are listed in the [setup.py](./setup.py)

## What parsers are currently implemented?

**Implemented and validated:**

- OpenDSS reader and writer
- CYME writer
- Gridlabd reader and writer

**Implemented but not validated:**

- CYME reader
- DEW reader

**To be added soon:**

- CIM reader and writer
- Synergy reader
- DEW writer

## How to get started

- Step 1: Git clone the repo:

```bash
git clone https://github.com/NREL/ditto ditto
```

- Step 2: Pip install DiTTo:

```bash
cd ./ditto
pip install -e .
```

- Step 3 (optional): Pip install OpenDSSDirect if you plan to use the OpenDSS reader:

```bash
pip install OpenDSSDirect.py
```

- Step 3: Run installation tests (Not implemented Yet)

## Basic Usage

The most common usage is when one has  a system in a given format, say OpenDSS, and wants to convert it to another format, say CYME. The convertion process will always be structured in the following way:

- Instanciate a store object which will store all the objects and attributes of your model

```python
from ditto.store import Store
m=Store()
```

- Instanciate a reader object with the required arguments. These arguments may vary depending on the format. For example, the OpenDSS reader expects a path for the master.dss file as well as a path for the buscoord.dss file.

```python
from ditto.readers.opendss.read import reader
opendss_reader=reader(master_file='/Users/johny_cash/IEEE_13_node/master.dss,
              		  buscoordinates_file='/Users/johny_cash/IEEE_13_node/buscoords.dss')
```

- Call the parse method of the reader with the store object as argument.

```python
opendss_reader.parse(m)
```

- Instanciate a writer object with the required arguments (output folder path…).

```python
from ditto.writers.cyme.write import writer
cyme_writer=writer(output_path='./', log_path='./')
```

- Call the write method of the writer with the store object as argument.

```python
cyme_writer.write(m)
```



## How is the code structured?

Here is a simplified view of the code structure (only the key components are displayed):

```reStructuredText
​```
DiTTo
│   README.md
│   docs
|   tests
│
└───ditto
    │   store.py
    │
    └───core
    |   │   base.py
    |   │   _factory.py
    |   │   exceptions.py
    |
    └───readers
    |   └───cyme
    |   |      |   read.py
    |   └───opendss
    |          |   read.py
    |
    └───writers
        └───cyme
        |      |   write.py
        └───opendss
               |   write.py
​```
```

Most of the code is located in the ditto directory. The core structure responsible for storing the objects is implemented in the core folder. Readers are implemented in readers and writers in writers. These two folders then contain the different format in different subfolders.

**Example 1:** The OpenDSS reader is located in:

```bash
DiTTo/ditto/readers/opendss/read.py
```

And can be imported with:

```python
from ditto.readers.opendss.read import reader
```

**Example 2:** The CYME writer is located in:

```bash
DiTTo/ditto/writers/cyme/write.py
```

And can be imported with:

```python
from ditto.writers.cyme.write import writer
```

