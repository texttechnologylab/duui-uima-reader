FROM nvidia/cuda:11.0.3-base-ubuntu20.04

RUN apt update && DEBIAN_FRONTEND=noninteractive \
    apt install --no-install-recommends -y build-essential software-properties-common curl && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt install --no-install-recommends -y python3.8 python3-pip python3-setuptools python3-distutils && \
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
ARG ANNIS_VERSION=3.3
ENV ANNIS_VERSION=$ANNIS_VERSION


# ---------------------------------------------------------
# ---------------------------------------------------------
# meta data
# ---------------------------------------------------------
# name
ARG TEXTIMAGER_ANNOTATOR_NAME="duui-annis_reader"
ENV TEXTIMAGER_ANNOTATOR_NAME=$TEXTIMAGER_ANNOTATOR_NAME
# version
ARG TEXTIMAGER_ANNOTATOR_VERSION=0.1
ENV TEXTIMAGER_ANNOTATOR_VERSION=$TEXTIMAGER_ANNOTATOR_VERSION

# service script
COPY ./requirements.txt ./requirements.txt


# requirements
RUN python3 -m pip install -r requirements.txt

COPY ./src/annis_utils ./annis_utils
COPY ./src/api_utils ./api_utils
COPY ./src/communication.lua ./communication.lua
COPY ./src/dkpro-core-types.xml ./dkpro-core-types.xml
COPY ./src/duui_annis_reader.py ./duui_annis_reader.py

# server
ENTRYPOINT ["uvicorn", "duui_annis_reader:app", "--host", "0.0.0.0", "--port", "9714"]
CMD ["--workers", "1"]