export ANN_VERSION=3.3

export TEXTIMAGER_ANNOTATOR_NAME=duui-annatto_reader
export TEXTIMAGER_ANNOTATOR_VERSION=0.1

docker build \
  --build-arg ANN_VERSION \
  --build-arg TEXTIMAGER_ANNOTATOR_NAME \
  --build-arg TEXTIMAGER_ANNOTATOR_VERSION \
  -t ${TEXTIMAGER_ANNOTATOR_NAME}:${TEXTIMAGER_ANNOTATOR_VERSION} \
  -f docker/Dockerfile \
  .