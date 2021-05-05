#!/bin/bash

# Helper script for adding release tags and creating GitHub releases.
# This script is meant to run in CircleCi org-global context
# Pass RELEASE_TYPE parameter: stage or prod

RELEASE_TYPE=$1

API_URL="https://api.github.com/repos/iamdavidzeng/iadz"

# Ignore stage

if ! [[ $RELEASE_TYPE = *'prod'* ]]; then
    exit
fi;

LAST_RELEASE_TAG=$(git tag --list 'v*' --sort=-v:refname | head -n 1)

if [ LAST_RELEASE_TAG ]; then
    NEW_RELEASE=$(echo $LAST_RELEASE_TAG | awk -F. '{print $1"."$2"."$3+1}');
else
    NEW_RELEASE="v1.0.0"
fi;

# GitHub Release

REQUEST_BODY=$(cat <<EOF
{
  "tag_name": "$NEW_RELEASE",
  "target_commitish": "$CIRCLE_SHA1",
  "name": "$NEW_RELEASE",
  "body": "",
  "draft": false,
  "prerelease": false
}
EOF
)

curl -XPOST \
-H "Authorization: token $GITHUB_AUTH_TOKEN" \
-d "$REQUEST_BODY" "$API_URL/releases"

