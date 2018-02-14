.. highlight:: shell

============
Installation
============


Stable release
--------------

To install the latest version of ditto from master for development, run this command in your terminal
after changing your directory to the folder where you'd like to set up the development:

.. code-block:: console

    pip install -e git+https://github.nrel.gov/FeederTools/ditto.git@master#egg=ditto

To install the latest version of ditto from master for usage, run this command in your terminal:

.. code-block:: console

    pip install git+https://github.nrel.gov/FeederTools/ditto.git@master

To install a specific stable version:

.. code-block:: console

    pip install git+https://github.nrel.gov/FeederTools/ditto.git@1.0.1

The above are the preferred methods to install ditto, as it will always install the most recent stable release. 

From sources
------------

The sources for ditto can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.nrel.gov/FeederTools/ditto

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.nrel.gov/FeederTools/ditto/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ pip install -e .

OR

.. code-block:: console

    $ python setup.py install # not recommended



.. _Github repo: https://github.nrel.gov/FeederTools/ditto
.. _tarball: https://github.nrel.gov/FeederTools/ditto/tarball/master
