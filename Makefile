SHELL := /bin/bash
ROOT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
export PATH := ${ROOT_DIR}/node_modules/.bin:$(PATH)

edit:
	atom ${ROOT_DIR}

build:
	npm run build

compile:
	npx tsc
	npx eslint .

open: compile
	open -na "Google Chrome" --args --new-tab "file://${ROOT_DIR}/templates/s3-${ITERATION}.htm"

~compile:
	npx tsc -w

~run:
	npx webpack serve --config webpack.config.js --open

serve:
	npm run serve

INTERPRET_TEMPLATE := ${ROOT_DIR}/.claude/skills/interpret-pattern/templates/pattern-interpretation.html

interpret:
	@if [ -z "$(SESSION)" ]; then echo "Usage: make interpret SESSION=<session-dir>"; exit 1; fi
	python3 ${ROOT_DIR}/tools/generate-interpretation.py "$(SESSION)" --template "${INTERPRET_TEMPLATE}"

SESSIONS_DIR := /Users/omareid/Dropbox/Data/sacred-patterns
GALLERY_DIR := ${ROOT_DIR}/site/gallery
GALLERY_TEMPLATE := ${ROOT_DIR}/.claude/skills/learn-new-pattern/templates/gallery-template.html
GALLERY_BUILDER := ${ROOT_DIR}/.claude/skills/learn-new-pattern/build-gallery-index.sh

gallery:
	@echo "Building gallery from sessions..."
	@mkdir -p ${GALLERY_DIR}
	@for session_dir in ${SESSIONS_DIR}/session-*/; do \
		session_name=$$(basename "$$session_dir") ; \
		if [ -f "$$session_dir/dashboard.html" ]; then \
			mkdir -p "${GALLERY_DIR}/$$session_name" ; \
			cp "$$session_dir/dashboard.html" "${GALLERY_DIR}/$$session_name/index.html" ; \
			echo "  Copied $$session_name dashboard" ; \
		fi ; \
		if [ -f "$$session_dir/final/timelapse.gif" ]; then \
			cp "$$session_dir/final/timelapse.gif" "${GALLERY_DIR}/$$session_name/timelapse.gif" ; \
			echo "  Copied $$session_name timelapse.gif" ; \
		fi ; \
		if [ -f "$$session_dir/final/timelapse.mp4" ]; then \
			cp "$$session_dir/final/timelapse.mp4" "${GALLERY_DIR}/$$session_name/timelapse.mp4" ; \
			echo "  Copied $$session_name timelapse.mp4" ; \
		fi ; \
	done
	@for drawing_dir in ${SESSIONS_DIR}/drawings/*/; do \
		if [ -d "$$drawing_dir" ]; then \
			drawing_name=$$(basename "$$drawing_dir") ; \
			if [ -f "$$drawing_dir/output.html" ]; then \
				mkdir -p "${GALLERY_DIR}/drawings/$$drawing_name" ; \
				cp "$$drawing_dir/output.html" "${GALLERY_DIR}/drawings/$$drawing_name/index.html" ; \
				echo "  Copied drawing $$drawing_name" ; \
			fi ; \
		fi ; \
	done
	@echo "Generating gallery index..."
	@bash ${GALLERY_BUILDER} ${SESSIONS_DIR} ${GALLERY_TEMPLATE} ${GALLERY_DIR}/index.html ${GALLERY_DIR}
	@echo "Gallery build complete."

deploy: build gallery
	@echo "Deploying site to gh-pages..."
	@DEPLOY_DIR=$$(mktemp -d) && \
	git worktree add "$$DEPLOY_DIR" gh-pages && \
	cp ${ROOT_DIR}/site/bundle.js "$$DEPLOY_DIR/bundle.js" && \
	cp ${ROOT_DIR}/site/index.html "$$DEPLOY_DIR/index.html" && \
	if [ -d "${GALLERY_DIR}" ]; then \
		cp -r ${GALLERY_DIR} "$$DEPLOY_DIR/gallery" ; \
	fi && \
	if [ -d "${ROOT_DIR}/templates/components" ]; then \
		cp -r ${ROOT_DIR}/templates/components "$$DEPLOY_DIR/components" ; \
	fi && \
	if [ -d "${ROOT_DIR}/tools/analysis" ]; then \
		mkdir -p "$$DEPLOY_DIR/tools/analysis" ; \
		cp ${ROOT_DIR}/tools/analysis/*.html "$$DEPLOY_DIR/tools/analysis/" ; \
		if [ -d "${ROOT_DIR}/tools/analysis/screenshots" ]; then \
			cp -r ${ROOT_DIR}/tools/analysis/screenshots "$$DEPLOY_DIR/tools/analysis/screenshots" ; \
		fi ; \
	fi && \
	cd "$$DEPLOY_DIR" && \
	git add -A && \
	git diff --cached --quiet || (git commit -m "Deploy site update" && git push origin gh-pages) && \
	cd ${ROOT_DIR} && \
	git worktree remove "$$DEPLOY_DIR" && \
	echo "Deployed to https://art.bytesofpurpose.com/"
