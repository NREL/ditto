## Installation

**Stable release**

To install the latest version of ditto from master for development, run this command in your terminal
after changing your directory to the folder where you'd like to set up the development:

```bash
$ pip install git+https://github.com/NREL/ditto.git@master#egg=ditto
```

To install the latest version of ditto from master for usage, run this command in your terminal:

```bash
$ pip install git+https://github.com/NREL/ditto.git@master
```

To install a specific stable version:

```bash
$ pip install git+https://github.com/NREL/ditto.git@1.0.1
```

The above are the preferred methods to install ditto, as it will always install the most recent stable release.

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
$ pip install -e .
```

OR

```bash
$ python setup.py install # not recommended
```

See the developer guide for instructions on how to add features to ditto.

