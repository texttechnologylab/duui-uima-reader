export TEXTIMAGER_ANNOTATOR_NAME=duui-pepper-reader
export TEXTIMAGER_ANNOTATOR_VERSION=0.1


docker build \
  -t ${TEXTIMAGER_ANNOTATOR_NAME}:${TEXTIMAGER_ANNOTATOR_VERSION} \
  -f docker/Dockerfile \
  .