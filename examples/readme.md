# DiTTo examples

DiTTo basic usage is the conversion from one format to another. This readme explains how a basic conversion can be done with the command line and with a Python script.

Conversion examples with more advanced features can be found in the examples sub-folders.

## Basic usage: Converting from one format to another

### Method 1: Through the command line

#### The convert command

DiTTo supports a command line interface (CLI) to quickly convert a model. The command is simply:

```bash
ditto convert
```

Help can be obtained using:

```bash
ditto convert --help
```

#### From and To

The options ```—from``` and ```—to``` are easy to understand, they just tell ```ditto convert``` what format is expected for the input, and what format is desired for the output. If we want to convert from opendss to gridlabd, we can use:

```bash
ditto convert --from opendss --to gridlabd
```

Note that, we can use short-cut names for the format like:

```bash
ditto convert --from dss --to glm
```

#### Input

In addition to the formats, we need to provide some input to DiTTo. The main issue here is that inputs are very different accross formats. It is common practice in OpenDSS for example to use master files to redirect all the other dss files, while a Cyme ASCII model is composed of three files: equipment, network, and loads. 

To be consistent, the CLI accepts only one file whatever the format. If we have a gridlabd model entirely stored in a file called ```model.glm``` we can use:

```bash
ditto convert --from glm --input ./model.glm --to cyme
```

For formats like Cyme where we need multiple input files, we need to write a simple JSON configuration file:

```json
!Content of config.json
{"data_folder_path": "/home/cyme_models/ieee_13node/",
 "network_filename": "net.txt",
 "equipment_filename": "equip.txt",
 "load_filename": "loads.txt"}
```

Which results in the following command:

```bash
ditto convert --from cyme --input ./config.json --to dss
```

#### Output

Finally, we need to tell ```ditto convert``` where to write the output. This is done with the ```—output``` option. Make sure to provide the path to the folder you want the files to be written in. For example, if we want to output in a folder named ```./results``` we do the following:

```bash
ditto convert --from cyme --input ./config.json --to dss --output ./results/
```

### Examples

#### Convert the IEEE 4 node from GridlabD to OpenDSS

Run the following command:

```bash
ditto convert --input ../tests/data/gridlabd/4node.glm --from glm --to dss --output ./
```

#### Convert the IEEE 13 node from OpenDSS to CYME

Here, we use the configuration file: ```ditto/documentation/ieee_13node_opendss_input.json```:

```bash
ditto convert --input ./ieee_13node_opendss_input.json --from opendss --to cyme --output ./
```

### Method 2: Writing a script

This is a more advanced method which provides more flexibility and enable the user to access all the functionality of DiTTo. The basic conversion scripts usually go through the following steps:

#### Step 1: Import the required modules

For basic conversion usage, we need to import a reader, a writer, and a ```Store``` object:

```python
#Import the reader
#...assuming we want to read from OpenDSS
from ditto.readers.opendss.read import Reader

#Import the writer
#...assuming we want to write to Cyme
from ditto.writers.cyme.write import Writer

#Import the Store
#...this will always be the same
from ditto.store import Store
```

#### Step 2: Instanciate an empty store

This step is pretty straightforward:

```python
model = Store()
```

#### Step 3: Instanciate a reader

This is probably the most delicate step because every reader is a bit different and expects various number of files. Refer to the documentation to know what needs to be provided. In this OpenDSS—>Cyme example, we need to provide a master file and a buscoordinate file to the OpenDSS reader:

```python
dss_reader = Reader(master_file="./dss_models/ieee_13node/master.dss",
                    buscoordinate_file="./dss_models/ieee_13node/buscoord.dss")
```

#### Step 4: Parse

This is also pretty simple. We just need to provide the emty ```Store``` object we created as an argument of the ```parse``` method. All readers implement a ```parse``` method:

```python
dss_reader.parse(model)
```

#### Step 5: Instanciate the writer

All writers are instanciated in the same way. We only need to provide the path to the output folder:

```python
cyme_writer = Writer(output_path="/results/ieee_13node/")
```

#### Step 6: Write

Simply use the ```write``` method implemented by all ditto writers. We just need to provide, once again, the ```Store``` object as an argument:

```python
cyme_writer.write(model)
```



