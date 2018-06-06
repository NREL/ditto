Installation
============

To develop `DiTTo`, you will need to follow the development instructions:


```bash
git clone https://github.com/NREL/ditto
pip install -e ".[dev]"
```

In addition to all the dependencies, this also installs the requirements for running tests.
Also, this installs auto code formatters, checks for trailing whitespace, checks for valid AST and checks for merge conflict markers.
The pre-commit hooks will not let you commit code that fails these checks.
Your code will automatically be formatted when you attempt to make a commit.
These auto formatted changes need to be explicitly added to the staging area in order for the commit to be created.
If you don't want to run the pre-commit hooks, you can make a commit using the `--no-verify` flag.

