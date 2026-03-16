ARG BASE_DOCKER_VERSION=torch2.4.1-cuda12.4
#########################################################################
FROM k2fsa/icefall:${BASE_DOCKER_VERSION}
# update to latest code
RUN git pull
# install local
RUN pip install -e .

