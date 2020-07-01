SHELL := /bin/bash
ROOT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
# https://stackoverflow.com/questions/8941110/how-i-could-add-dir-to-path-in-makefile
export PATH := ${ROOT_DIR}/node_modules/.bin:$(PATH)
tsc := ${ROOT_DIR}/node_modules/.bin/tsc

edit:
	atom ${ROOT_DIR}

_build:
	npm run build

build: _build
	docker build -t sacred-patterns .

compile:
	npx tsc
	# https://www.cyberciti.biz/faq/find-command-exclude-ignore-files/
	# find . -type f \( -iname "*.ts" ! -iname ".*" ! -path "./node_modules*" ! -path "./site*" \) -exec eslint {} \;
	npx eslint . --ext .ts,.tsx

open: compile
	open -na "Google Chrome" --args --new-tab "file://${ROOT_DIR}/templates/s3-${ITERATION}.htm"

~compile:
	npx tsc -w

_run:
	# Ensure container is  running ... or run it ...
	(docker ps -f ancestor=sacred-patterns -f status=running -n 1 -q | grep -v '^$$') || \
		docker logs $$( docker run -d -v ${ROOT_DIR}/site:/site/site -p 3001:3000 sacred-patterns:latest ; sleep 1 )

run: _run
	open -a "Google Chrome" http://localhost:3001

stop:
	docker ps -f ancestor=sacred-patterns -f status=running -n 1 -q | xargs -n 1 docker stop

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
