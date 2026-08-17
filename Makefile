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

# Cross-repo tenet 12 — dependency vulnerability surface (sacred-patterns#346)
# Report-only (exit 0 even on findings) — gating is intentional follow-on (#346 → #343).
# Currently clean (0 vulns); kept report-only so adding it to a CI gate later is a
# one-line change (`-npm audit` → `npm audit`).
# === Gate parity ===
#
# This repo has no CI. Nothing runs on a push or a pull request; every enforced
# check is a git hook, each hook sees only what one commit stages, and
# `--no-verify` skips all of them. `local.ci` is what runs the same gates over
# the whole tree — plus the five checks that exist here and no hook runs at all.
#
# The name is borrowed on purpose. There is no CI here to be parity *with*, and
# calling this `local.ci` is how somebody who learned the name in bikar or qiyas
# finds it. The output says plainly that there is no remote counterpart, so the
# name cannot be read as a claim that something else also ran.

local.check-gate-parity: ## Fail if any git-hook gate is missing from gate-parity.yaml
	@python3 ${ROOT_DIR}/scripts/gate_parity.py --check

local.gate-parity: local.check-gate-parity ## Run every hook gate's wholesale form
	@python3 ${ROOT_DIR}/scripts/gate_parity.py --run

local.ci: local.check-gate-parity ## Every hook gate over the whole tree, plus the checks no hook runs
	@python3 ${ROOT_DIR}/scripts/gate_parity.py --run --with-local-only

local.ci-strict: local.check-gate-parity ## As local.ci, but an unverifiable gate is a failure
	@python3 ${ROOT_DIR}/scripts/gate_parity.py --run --with-local-only --strict

audit:
	-npm audit
	@echo "[audit] npm audit complete (report-only)"

# Cross-repo tenet 12 — secret surface (sacred-patterns#345).
# Strict (no `-` prefix): history is currently clean. A leak ever entering
# history must fail loudly; report-only would defeat the gate.
# Install: brew install gitleaks
gitleaks:
	gitleaks detect --no-banner --redact

# Cross-repo tenet 12 — SAST (sacred-patterns#347).
# Strict (no `-` prefix): any finding is either a regression or a real issue and
# must surface loudly; report-only would defeat the gate.
# This comment used to say "src/ + tools/ are currently clean (0 findings at
# baseline)". Nothing ran the scanner after that was written — no hook triggers
# on tools/ — so nothing rechecked it. The first run through gate-parity.yaml
# (2026-08-17) returned rc=2 on one: a dynamic urllib.request.urlopen in
# tools/weave-only-compare.py. Left red rather than baselined away.
# Install: pip install semgrep
semgrep:
	semgrep --config=p/typescript --config=p/security-audit --error --quiet --metrics=off src tools

# Cross-repo tenet 12 — typo surface (sacred-patterns#349).
# Strict (no `-` prefix). src/ts + tools/ + docs were triaged to 0 at the
# sacred-patterns#349 baseline by fixing src/ts/index.ts:60 (shfit → shift), and
# have drifted since: the first run through gate-parity.yaml (2026-08-17) found
# 11, ten of them in tools/wave-plan-server.py. No hook trigger reaches tools/,
# so nothing had re-run this. Left red. `ans` is a legitimate variable
# name (user-answer prompt) in tools/auto-iterate*.py; codespell flags it as
# "and" — suppressed via -L ans. Other suppressions, all legitimate words
# codespell misreads: `Couter` (DSL circle identifier C-outer quoted in
# decision docs), `SME` (subject-matter expert, tenet text), `pre-selected`
# (valid hyphenation, tenet + picker text). src/js/ is gitignored TypeScript
# build output (mirrors eslint config ignore). Mirrors qiyas local.spelling
# + bikar wiring. Install: pip install codespell
spelling:
	codespell -L ans,couter,sme,pre-selected --skip="src/js,node_modules,site" src tools .claude docs CLAUDE.md README.md REFERENCES.md

# tools/ test harness — stdlib unittest, not pytest: the system python3 these
# tools run under has no pytest, and the tools themselves are stdlib-only by
# convention (see tools/portal_verdict.py docstring). The cross-repo end-to-end
# test self-skips when uv or the qiyas repo is absent.
# Wired to nothing, and red: 3 of 63 fail on committed master as of 2026-08-17
# (test_studio_field_defaults_bounded.py). Reachable only through `make local.ci`.
tool-tests:
	python3 -m unittest discover -s tools/tests -v

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
