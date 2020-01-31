SHELL := /bin/bash
ROOT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
ITERATION := i7

build:
	npx webpack --config webpack.config.js

compile:
	find ${ROOT_DIR}/${ITERATION}/ -name '*.js' -exec eslint {} \;

open: compile
	open -na "Google Chrome" --args --new-tab "file://${ROOT_DIR}/${ITERATION}/s3-${ITERATION}.htm"
