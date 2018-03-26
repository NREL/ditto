# Validation

## Structure

The validation folder is structured in the following way:

### Inputs

Input models are stored in the inputs folder with the following logic:

		./inputs/{format}/{feeder}

{format} should be replaced by opendss, cyme, gridlabd... (lower case convention)

For example the OpenDSS model of the IEEE 123 node feeder would be in ./inputs/opendss/ieee_123_node/

### Outputs

Output are stored in the inputs folder with the following logic:

		./outputs/{format_from}/{format_to}/{feeder}

For example the output of the OpenDSS--->DiTTo--->CYME conversion process on the IEEE 13 node feeder would be stored in ./outputs/from_opendss/to_cyme/ieee_13_node/

### Logs

#### Structure and name convention

Log files are stored in the log folder with the following logic:

		./logs/reader/{format}/{feeder}

		./logs/writer/{format}/{feeder}

Log file names have a time stamp in 'H_M_d_m_Y' format (this can be changed in converter.py).

#### Managing log files

Since log files can accumulate very quickly, clean_logs.py implements a tool to manage them.

There are two ways to use this module:

- Remove all log files:

```bash
$ python clean_logs.py
```

- Remove only a subset of the log files:

```bash
$ python clean_logs.py -f ./logs/reader/opendss
```

This will remove all OpenDSS reader log files for example.

```bash
$ python clean_logs.py -f ./logs/writer
```

This will remove all writer log files.

Note: Names of removed files are printed when they are deleted.

### Notebooks

Notebooks related to validation are stored in the notebooks folder.

## Validation method

### Step 1: Conversion

This is done by using parse.py (which uses converter.py). A command line interface can be used in the following way:

```bash
$ python parse.py -f ieee_13_node -b opendss -a cyme
```

This will parse the IEEE 13 node feeder from OpenDSS format to DiTTo and export to CYME format.

It is possible to provide multiple feeders and/or formats:

```bash
$ python parse.py -f ieee_13_node -f ieee_123_node -b opendss -a cyme -a gridlabd
```

It is also possible to run all possible conversion with:

```bash
$ python parse.py
```

### Step 2: Power Flows

This is the tricky step because we do not have easy ways to run power flow analysis on most commercial formats like CYME or DEW.

Currently, only OpenDSS is supported in the run_power_flow module.

Again, it can be used through the command line:

```bash
$ python run_power_flow.py -f ieee_13_node -f ieee_123_node
```

This will run all power flow analysis on all possible 13 node and 123 node feeders in the validation subfolder (inputs and outputs).

Since we can do this only in OpenDSS for now, this command will run on the following feeders:

	- ./inputs/opendss/ieee_13_node
	- ./inputs/opendss/ieee_123_node
	- ./outputs/from_*/to_opendss/ieee_13_node
	- ./outputs/from_*/to_opendss/ieee_123_node

Results are stored in the same folder as the feeder under the name "voltage_profile.csv"

### Step 3: Comparison metrics

Compare the power flow results.

```bash
$ python compare.py -p1 ./inputs/opendss/ieee_13_node -p2 ./outputs/from_cyme/to_opendss/ieee_13_node
```

This will look for "voltage_profile.csv" in both directories and load them into a Pandas dataframe.

For now, this only computes the root mean square error for each phase (in p.u).
