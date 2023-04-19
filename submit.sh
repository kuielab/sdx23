#!/bin/bash

set -e

REPO_ROOT_DIR=$(git rev-parse --show-toplevel)

log_info() {
  echo -e "\033[0;36m$@\033[0m"
}

log_success() {
  echo -e "\033[0;32m$@\033[0m"
}

log_normal() {
  echo -e "$@"
}

log_error() {
  >&2 echo -e "\033[0;31m$@\033[0m"
}

print_usage() {
cat << USAGE
Utility script to make submissions. 
It adds current working directory files, setup lfs, commit and upload it to AIcrowd GitLab.

Usage: ./submit.sh <unique-submission-name>

Example:
./submit.sh "bayes-v0.1"

Prerequisite:
Install aicrowd-cli and login on AIcrowd
#> pip install -U aicrowd-cli
#> aicrowd login

USAGE
}


bad_remote_message() {
  log_error "AIcrowd remote not found"
  log_error "It should have been automatically set, but given it isn't. Please run \`git remote add aicrowd git@gitlab.aicrowd.com:<username>/sdx-2023-music-demixing-track-starter-kit.git\` manually."
  exit 1
}

get_submission_remote() {
  echo "aicrowd"
}

get_submission_remote_url() {
  git remote get-url aicrowd
}

check_remote() {
  log_info Checking git remote settings...
  get_submission_remote > /dev/null
  log_success Using $(get_submission_remote_url | awk -F'@' '{print $NF}' | sed 's|\.git||g') as the submission repository
}


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
  REMOTE=$(get_submission_remote)
  TAG=$(echo "$@" | sed 's/ /-/g')
  git add --all
  git commit -m "Changes for submission-$TAG" || true  # don't exit when no new commits are there
  git push $REMOTE master
  git tag -am "submission-$TAG" "submission-$TAG"
  git push $REMOTE "submission-$TAG"
  log_success "Check the submission progress in your repository: $(get_submission_remote_url | awk -F'@' '{print $NF}' | sed 's|\.git||g')/issues"
}

check_cli_install() {
  set +e
  which aicrowd > /dev/null
  retval=$?
  if [ $retval -ne 0 ]; then
    log_error 'Please install AIcrowd CLI using `pip install -U aicrowd-cli`';exit 1
  fi
  python -c 'from aicrowd.contexts.config import CLIConfig;c=CLIConfig();c.load(None);exit(1) if c.get("aicrowd_api_key") is None else True'
  retval=$?
  if [ $retval -ne 0 ]; then
    log_error 'Please login to AIcrowd using `aicrowd login`';exit 1
  fi
  export USERNAME=$(python -c 'from aicrowd.contexts.config import CLIConfig;c=CLIConfig();c.load(None);print(c.get("gitlab")["username"])')
  retval=$?
  if [ $retval -ne 0 ]; then
    log_error 'You might be on older AIcrowd CLI version. Please upgrade using `pip install -U aicrowd-cli` and login again.';exit 1
  fi
  export OAUTH=$(python -c 'from aicrowd.contexts.config import CLIConfig;c=CLIConfig();c.load(None);print(c.get("gitlab")["oauth_token"])')
  git remote add aicrowd https://oauth2:$OAUTH@gitlab.aicrowd.com/$USERNAME/sdx-2023-music-demixing-track-starter-kit.git 2> /dev/null
  git config lfs.https://oauth2:$OAUTH@gitlab.aicrowd.com/$USERNAME/sdx-2023-music-demixing-track-starter-kit.git/info/lfs.locksverify true
  git config lfs.https://gitlab.aicrowd.com/$USERNAME/sdx-2023-music-demixing-track-starter-kit.git/info/lfs.locksverify true
  retval=$?
  if [ $retval -ne 0 ]; then
    log_normal "Remote already exit, repository location: $(get_submission_remote | awk -F'@' '{print $NF}' | sed 's|\.git||g')";
  fi
  git config --global user.email > /dev/null
  retval=$?
  if [ $retval -ne 0 ]; then
    export GITID=$(python -c 'from aicrowd.contexts.config import CLIConfig;c=CLIConfig();c.load(None);print(c.get("gitlab")["userid"])')
    log_normal "Git setup dont have email defined, setting it to \"${GITID}-${USERNAME}@users.noreply.gitlab.aicrowd.com\""
    git config --global user.email "${GITID}-${USERNAME}@users.noreply.gitlab.aicrowd.com"
    git config --global user.name $USERNAME
  fi
  log_success "Making submission as \"${USERNAME}\""
  set -e
}

submit() {
  check_cli_install
  check_remote
  setup_lfs "$@"
  setup_commits "$@"
}

if [[ $# -lt 1 ]]; then
  print_usage
  exit 1
fi

submit "$@"
