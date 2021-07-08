#!/bin/bash

REPO="ghcr.io/mbeham/public_containers"

for dir in simplewebserver ; do

  pushd $dir
  docker build -t $REPO/$dir:latest .
  docker push $REPO/$dir:latest
  popd

done

