#!/usr/bin/env bash

set -e

D3A_IMAGE_TAG="gsy-e-tests"

if [[ "$(docker images -q ${D3A_IMAGE_TAG} 2> /dev/null)" == "" ]]; then
  echo "Building d3a image ..." && \
  rm -rf tests/gsy-e && \
  cd tests/ && \
  git clone -b feature/D3ASIM-3669 https://github.com/faizan2590/gsy-e.git && \
  cd gsy-e && \
  docker build -t ${D3A_IMAGE_TAG} . && \
  cd ../ && \
  rm -rf gsy-e/ && \
  cd ../ && \
  echo ".. done"
fi
