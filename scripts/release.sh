#!/bin/bash
# based on docs here: https://heigit.atlassian.net/wiki/spaces/OQT/pages/3474149/Releases
# requires local installation of `gh`, the github CLI: https://cli.github.com



# please adjust these version names first
export OLD_VERSION=1.8.1
export NEW_VERSION=1.8.2


# exit immediately if a command exits with a non-zero status
set -e


# get the directory of the current script
SCRIPT_DIR="$(dirname "$0")"

# import user prompt
source "$SCRIPT_DIR/functions.sh"


prompt_user "👉 did you adjust the values for old and new versions in the release script?"


prompt_user "👉 do you run this script in an active python env? if not run 'poetry shell' first"


# change to main directory
cd $SCRIPT_DIR/..


# get latest version of main and create new branch
prompt_user "👉 create release branch?"
git checkout main
git pull
git checkout -b "release-$NEW_VERSION"
echo "✅ created release branch of the latest main"


# update to latest version of swagger libs
prompt_user "👉 update swagger?"
./scripts/update_swagger_scripts.sh
echo "✅ updated to latest version of swagger libs"


# Update version in pyproject.toml
prompt_user "👉 update project version?"
poetry version "$NEW_VERSION"
echo "✅ updated project version in pyproject.toml to $NEW_VERSION"


# update version in __init__.py
prompt_user "👉 update __init__.py?"
export OLD="__version__ = \"$OLD_VERSION\""
export NEW="__version__ = \"$NEW_VERSION\""


# might not work like this on linux
run_sed "s/$OLD/$NEW/g" ohsome_quality_api/__init__.py
rm -rf ohsome_quality_api/__init__.py.bak
echo "✅ updated __init__.py to $NEW_VERSION"


# insert new sub-headline for new release
prompt_user "👉 update CHANGELOG.md?"
run_sed "s/## Current Main/## Current Main\n\n## Release  $NEW_VERSION/g" CHANGELOG.md
rm -rf CHANGELOG.md.bak
echo "✅ updated CHANGELOG.md"


prompt_user "👉 commit and push all changed files?"
git add pyproject.toml
git add ohsome_quality_api/__init__.py
git add tests/integrationtests/fixtures/vcr_cassettes/*
git add CHANGELOG.md
git add scripts/release.sh
git add ohsome_quality_api/api/static/*

git commit -m "prepare release $NEW_VERSION"
git push --set-upstream origin "release-$NEW_VERSION"
echo "✅ committed and pushed all changed files"


# create PR
prompt_user "👉 create PR?"
gh pr create --title "release new version $NEW_VERSION" --body "This PR is used for the Oqapi release process."
echo "✅ created new PR for the release"


# get PR approved
prompt_user "⚠️ Please check swagger docs and have PR approved - hit <y> when ready!"


prompt_user "👉 merge approved PR?"
gh pr merge --rebase
echo "✅ rebased the release PR into main"


git checkout main
git pull


# create github release and corresponding tag
prompt_user "👉 create github release and tag?"
export ANCHOR="release--${NEW_VERSION//\./}"
gh release create "$NEW_VERSION" -t "$NEW_VERSION" -n "See the [changelog](https://github.com/GIScience/ohsome-quality-api/blob/main/CHANGELOG.md#$ANCHOR) for release details."
echo "✅ created new github release and tag for version: $NEW_VERSION"



JENKINS_URL="https://jenkins.heigit.org/job/OQAPI/view/tags/job/${NEW_VERSION}/"
echo "⚠️ Please start the Jenkins tag build here: ${JENKINS_URL}"
run_open "$JENKINS_URL"
