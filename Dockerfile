# Build ditto
# docker build . -t ditto

# Run ditto
# docker run --rm -ti ditto --help

# https://hub.docker.com/_/python
FROM python:3.6-slim

# Install latest version of ditto
COPY ./ $HOME/ditto
WORKDIR $HOME/ditto

# Install ditto dependencies
RUN python -m pip install --upgrade pip && \
pip install -e .[all] && \
pip install pytest

# Validate install
RUN pytest -sv
RUN ditto --help

# By using an ENTRYPOINT, all of the arguments to docker
# run following the image name are passed as arguments
ENTRYPOINT [ "ditto" ]