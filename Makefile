all: clean test

clean:
	find . | grep -E "\(__pycache__|\.pyc|\.pyo$\)" | xargs rm -rf

test:
	PYTHONPATH=. py.test -vv --cov=ditto tests
