# Build ditto
# docker build . -t ditto

# Run ditto
# docker run --rm -ti ditto --help

# https://hub.docker.com/_/python
FROM python:3.6-slim-bullseye

# Install latest version of ditto
RUN apt-get update; apt-get install -y git
RUN git clone --depth 1 https://github.com/NREL/ditto.git
WORKDIR ditto

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