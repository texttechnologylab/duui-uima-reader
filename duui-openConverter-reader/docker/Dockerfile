FROM nvidia/cuda:11.0.3-base-ubuntu20.04

RUN apt update && DEBIAN_FRONTEND=noninteractive \
    apt install --no-install-recommends -y \
    build-essential software-properties-common curl \
    # Install OpenJDK 11 (JRE or JDK, depending on needs)
    openjdk-11-jre && \
    # Python dependencies
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt install --no-install-recommends -y \
    python3.8 python3-pip python3-setuptools python3-distutils && \
    apt clean && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3 /usr/bin/python
RUN python -m pip install --upgrade pip

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

WORKDIR /usr/src/app

EXPOSE 9714

# ---------------------------------------------------------
# config
# ---------------------------------------------------------
# annis-Version:
ARG OC_VERSION=0.1
ENV OC_VERSION=$OC_VERSION


# ---------------------------------------------------------
# ---------------------------------------------------------
# meta data
# ---------------------------------------------------------
# name
ARG TEXTIMAGER_ANNOTATOR_NAME="duui-openconvert_reader"
ENV TEXTIMAGER_ANNOTATOR_NAME=$TEXTIMAGER_ANNOTATOR_NAME
# version
ARG TEXTIMAGER_ANNOTATOR_VERSION=0.1
ENV TEXTIMAGER_ANNOTATOR_VERSION=$TEXTIMAGER_ANNOTATOR_VERSION

# service script
COPY ./requirements.txt ./requirements.txt


# requirements
RUN python3 -m pip install -r requirements.txt

COPY ./src/ocw ./src/ocw
COPY ./src/communication.lua ./src/communication.lua
COPY ./src/dkpro-core-types.xml ./src/dkpro-core-types.xml
COPY ./src/duui_openConverter.py ./src/duui_openConverter.py
COPY ./OpenConvert ./OpenConvert

WORKDIR /usr/src/app/src

# server
ENTRYPOINT ["uvicorn", "duui_openConverter:app", "--host", "0.0.0.0", "--port", "9714"]
CMD ["--workers", "1"]