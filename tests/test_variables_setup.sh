#!/usr/bin/env bash

# In this script, the necessary variables to execute the integration tests
# for gsy-myco-sdk both locally and remotely are described, configured and
# exported as environment variables for their further use.

# TODO: SETUP VARIABLES AS DESIRED AND RUN ABOVE LINE BEFORE EXECUTING TESTS
# $ source tests/test_variables_setup.sh

set -a

# (Optional) Path to local GBIT repository / URL to remote GBIT repository.
# Used during tox testenvs execution [ci, integrationtests]
# Serves to clone from local repo instead of remote.
# Defaults to URL of remote repository.
# INTEGRATION_TESTS_REPO="/Users/GSy/Workspace/gsy-backend-integration-tests"
INTEGRATION_TESTS_REPO=""

# (Optional) GBIT branch to clone integration tests from.
# Used during tox testenv execution [ci]
# Serves to specify checkout branch when cloning GBIT repo, if needed.
# Defaults to master branch.
# INTEGRATION_TESTS_BRANCH="feature/GSYE-194"
INTEGRATION_TESTS_BRANCH=""

# (Optional) Path to local GSY repository / URL to remote GSY repository.
# Used during tox testenvs execution on GBIT repository
# [test-gsy-e, test-gsy-web, test-gsy-e-sdk, test-gsy-myco-sdk]
# Serves to clone from local repo instead of remote.
# Defaults to remote repository.
# TARGET_REPO="/Users/GSy/Workspace/gsy-e-sdk" (gsy-e, gsy-web, gsy-myco-sdk)
TARGET_REPO=""

# (Optional) Branch to clone GSY repository from.
# Used during tox testenvs execution on GBIT repository
# [test-gsy-e, test-gsy-web, test-gsy-e-sdk, test-gsy-myco-sdk]
# Serves to specify checkout branch when cloning GSY repo, if needed.
# Defaults to master.
# TARGET_REPO="feature/GSYE-194" (gsy-web, gsy-e-sdk, gsy-myco-sdk)
BRANCH="" # editor's suggestion: rename to TARGET_BRANCH to match with TARGET_REPO

# (Optional) Branch to pip-install GSY-FRAMEWORK from.
# Used during tox testenvs execution on GBIT repository
# [test-gsy-e, test-gsy-web, test-gsy-e-sdk, test-gsy-myco-sdk]
# Serves to specify branch to pip-install GSY-FRAMEWORK from, if needed.
# Defaults to master.
# GSY_FRAMEWORK_BRANCH="D3ASIM-3669" (gsy-web, gsy-e-sdk, gsy-myco-sdk)
GSY_FRAMEWORK_BRANCH=""

# (Optional) Path to local repository to build GSYE image from.
# Used during docker image buildup after integration tests execution
# on GSYE-SDK & GSY-MYCO-SDK repositories.
# Serves to clone from local GSYE repo instead of remote.
# Defaults to remote repository.
# LOCAL_GSYE_IMAGE="/Users/GSy/Workspace/gsy-e"
LOCAL_GSYE_IMAGE=""


# (Optional) Branch to build GSYE image from.
# Used during docker image buildup after integration tests execution
# on GSYE-SDK & GSY-MYCO-SDK repositories.
# Serves to specify GSYE branch to build docker image from.
# Defaults to INTEGRATION_TESTS_BRANCH if set, else master.
# GSYE_IMAGE_BRANCH="feature/GSYE-201"
GSYE_IMAGE_BRANCH=""
