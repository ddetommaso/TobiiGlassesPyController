FROM python:3.8
LABEL maintainer="Davide De Tommaso <davide.detommaso@iit.it>"

ARG TOBIIGLASSESCTRL_VER

RUN adduser --disabled-password docky

USER docky

WORKDIR /home/docky


ENV PATH=${PATH}:/home/docky/.local/bin

USER docky

RUN cd $HOME &&\
    git clone --recursive https://github.com/ddetommaso/TobiiGlassesPyController &&\
    cd TobiiGlassesPyController &&\
    git checkout ${TOBIIGLASSESCTRL_VER} &&\
    pip3 install --user .
