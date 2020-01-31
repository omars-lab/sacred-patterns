SHELL := /bin/bash
ROOT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

build:
	npm run build

compile:
	find ${ROOT_DIR}/ -name '*.js' -exec eslint {} \;
	tsc
	eslint *.js

open: compile
	open -na "Google Chrome" --args --new-tab "file://${ROOT_DIR}/templates/s3-${ITERATION}.htm"

~compile:
	tsc -w

 # typescript
 # @types/lodash
 # @types/d3
 # express
 # webpack
 # webpack-cli
 # lodash
 # typescript
 # ts-loader
 # html-webpack-plugin
 # webpack
 # webpack-cli
