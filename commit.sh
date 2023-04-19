#!/bin/bash

set -e

REPO_ROOT_DIR=$(git rev-parse --show-toplevel)


setup_lfs() {
  git lfs install
  find * -type f -size +5M -exec git lfs track {} &> /dev/null \;
  set +e
  git ls-files -om | grep ".gitattributes" &> /dev/null \
    && git add .gitattributes \
    && git commit -m "auto: tracking new files via LFS" &> /dev/null
  set -e
}


setup_commits() {
  MESSAGE=$(echo "$@" | sed 's/ /-/g')
  git add --all
  git commit -m "$MESSAGE"
}

submit() {
  setup_lfs "$@"
  setup_commits "$@"
}

submit "$@"