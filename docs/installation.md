## Installation

**Stable release**

To install the latest version of ditto from master for development, run this command in your terminal
after changing your directory to the folder where you'd like to set up the development:

```bash
$ pip install git+https://github.com/NREL/ditto.git@master#egg=ditto[all]
```

**From sources**

The sources for ditto can be downloaded from the [Github repo](https://github.com/NREL/ditto).

You can either clone the public repository:

```bash
$ git clone git://github.com/NREL/ditto
```

Or download the [tarball](https://github.com/NREL/ditto/tarball/master):

```bash
$ curl  -OL https://github.com/NREL/ditto/tarball/master
```

Once you have a copy of the source, you can install it with:

```bash
$ pip install -e .[all]
```

See the developer guide for instructions on how to add features to ditto.

**Install specific packages alone**

If you want specific packages alone, you will be able to do the following:

```bash
$ pip install git+https://github.com/NREL/ditto.git@master#egg=ditto
$ ditto list --readers
$ ditto list --writers
$ pip install git+https://github.com/NREL/ditto.git@master#egg=ditto[opendss,gridlabd]
```
