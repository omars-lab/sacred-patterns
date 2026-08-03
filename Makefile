SHELL := /bin/bash
ROOT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
# https://stackoverflow.com/questions/8941110/how-i-could-add-dir-to-path-in-makefile
export PATH := ${ROOT_DIR}/node_modules/.bin:$(PATH)

tsc := ${ROOT_DIR}/node_modules/.bin/tsc

clean:
	npm run clean

compile:
	# https://www.cyberciti.biz/faq/find-command-exclude-ignore-files/
	# find . -type f \( -iname "*.ts" ! -iname ".*" ! -path "./node_modules*" ! -path "./site*" \) -exec eslint {} \;
	npm run compile

build:
	npm run build

edit:
	vscode ${ROOT_DIR}

open: compile
	open -na "Google Chrome" --args --new-tab "file://${ROOT_DIR}/templates/s3-${ITERATION}.htm"

run: compile build 
	node app/runner.js

# Recompilation Commands
compile.~:
	npx tsc -w

build.~:
	# https://stackoverflow.com/questions/38089785/webpack-watch-vs-hot-whats-the-difference
	npx webpack --watch --config webpack.config.js

run.lite.~:
	npx nodemon -w templates -w src/ts --ext 'ts tpl' --exec 'node app/runner.js'

run.~:
	npx nodemon -w templates -w src/ts --ext 'ts tpl' --exec 'make compile; make _build; node app/runner.js'

# Container Oriented Commands
build.container: 
	docker build -t sacred-patterns .

run.container: build.container
	# Ensure container is  running ... or run it ...
	(docker ps -f ancestor=sacred-patterns -f status=running -n 1 -q | grep -v '^$$') || \
		docker logs $$( docker run -d -v ${ROOT_DIR}/site:/site/site -p 3001:3000 sacred-patterns:latest ; sleep 1 )

stop.container:
	docker ps -f ancestor=sacred-patterns -f status=running -n 1 -q | xargs -n 1 docker stop

open.container: _run
	open -a "Google Chrome" http://localhost:3001

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


# https://webpack.js.org/guides/typescript/
# https://webpack.js.org/loaders/style-loader/
# https://stackoverflow.com/questions/30371000/react-bootstrap-using-webpack
# https://stackblitz.com/edit/react-ts-ig9rjb?file=package.json