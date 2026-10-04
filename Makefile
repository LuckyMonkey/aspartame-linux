PROFILE := $(CURDIR)/archiso/aspartame
BUILD_ROOT ?= /media/freezer/SteamLibrary/vms/aspartame-build
OUT_DIR ?= $(BUILD_ROOT)/artifacts/out
WORK_DIR ?= $(BUILD_ROOT)/artifacts/work

.PHONY: iso run rebuild-run clean test mdm-check mdm-run snakepit-qualify snakepit-launch-check snakepit-dependency-tension snakepit-dependency-pair snakepit-check qemu-macro sugar-info sugar-reload sugar-session-restart sugar-logs sugar-screenshot sugar-visual-check sugar-patch-check sugar-open-control-panel sugar-upstream-sync sugar-gtk4-init sugar-gtk4-build sugar-gtk4-run sugar-gtk4-smoke sugar-gtk4-check sugar-gtk4-update sugar-gtk4-status sugar-gtk4-series-check sugar-modernization-check activity-review-inventory activity-review-check activity-contract-check activity-matrix-check count-deploy

iso:
	./scripts/build-in-arch-root.sh

run:
	./scripts/run-qemu.sh

rebuild-run: clean iso run

clean:
	./scripts/clean.sh

test:
	./scripts/smoke-test.sh
	$(MAKE) activity-matrix-check
	python3 -m pytest -q tests

mdm-check:
	python3 -m py_compile management/server.py management/agent.py management/test_server.py
	(cd management && python3 test_server.py)

mdm-run:
	python3 -m management.server --bind 127.0.0.1 --port $${PORT:-8787}

snakepit-check:
	python3 -m py_compile scripts/snakepit.py

qemu-macro:
	ASPARTAME_QEMU_QMP=$${ASPARTAME_QEMU_QMP:-/tmp/aspartame-qemu-qmp-headless} \
		./scripts/qemu-headless-macro.py $(MACRO)

snakepit-qualify:
	python3 scripts/snakepit.py qualify \
		--software aspartame-management \
		--source management \
		--environment $${SNAKEPIT_ENVIRONMENT:-/tmp/aspartame-snakepit-management} \
		--record $${SNAKEPIT_RECORD:-reports/python/aspartame-management.json} \
		--target $${SNAKEPIT_TARGET:-host-development} \
		--reuse \
		--launchable \
		--command python -m unittest test_server

snakepit-launch-check: snakepit-qualify
	python3 scripts/snakepit.py launch \
		--record reports/python/aspartame-management.json

snakepit-dependency-tension:
	@if python3 scripts/snakepit.py qualify \
		--software dependency-tension-specimen \
		--source tests/fixtures/snakepit/dependency-tension \
		--environment /tmp/aspartame-snakepit-dependency-tension \
		--record reports/python/dependency-tension-20261002.json \
		--target host-development \
		--command python -m probe; then \
		echo "unexpected dependency-tension qualification pass" >&2; \
		exit 1; \
	else \
		status=$$?; test $$status -eq 1; \
	fi

snakepit-dependency-pair:
	@set -eu; pair_root=$$(mktemp -d /tmp/aspartame-snakepit-pair.XXXXXX); trap 'rm -rf "$$pair_root"' EXIT; \
	python3 scripts/snakepit.py qualify \
		--software dependency-pair-left \
		--source tests/fixtures/snakepit/dependency-pair/app-left \
		--environment "$$pair_root/left" \
		--record reports/python/dependency-pair-left-20261002.json \
		--install-requirements \
		--target host-development \
		--command python -m probe; \
	python3 scripts/snakepit.py qualify \
		--software dependency-pair-right \
		--source tests/fixtures/snakepit/dependency-pair/app-right \
		--environment "$$pair_root/right" \
		--record reports/python/dependency-pair-right-20261002.json \
		--install-requirements \
		--target host-development \
		--command python -m probe

sugar-info:
	./scripts/sugar-info.sh

sugar-reload:
	./scripts/sugar-reload.sh

sugar-session-restart:
	./scripts/sugar-session-restart.sh

sugar-logs:
	./scripts/sugar-logs.sh

sugar-screenshot:
	./scripts/sugar-screenshot.sh

sugar-visual-check:
	./scripts/sugar-visual-check.sh

sugar-patch-check:
	./scripts/sugar-patch.sh check

sugar-open-control-panel:
	./scripts/sugar-open-control-panel.sh

sugar-upstream-sync:
	./scripts/sugar-upstream-sync.sh $(CHECKOUTS)

sugar-gtk4-smoke:
	./scripts/sugar-gtk4-smoke.sh

sugar-gtk4-init:
	./scripts/sugar-gtk4-init.sh

sugar-gtk4-build:
	./scripts/sugar-gtk4-build.sh

sugar-gtk4-run:
	./scripts/sugar-gtk4-run.sh

sugar-gtk4-check:
	./scripts/sugar-gtk4-check.sh

sugar-gtk4-update:
	./scripts/sugar-gtk4-update.sh

sugar-gtk4-status:
	./scripts/sugar-gtk4-upstream-status.sh

sugar-gtk4-series-check:
	./scripts/sugar-gtk4-series-check.sh

activity-review-inventory:
	./scripts/activity-review-inventory.py

activity-review-check:
	./scripts/activity-review-check.sh

activity-review-capture:
	./scripts/activity-review-capture.sh $(ACTIVITY)

activity-contract-check:
	./scripts/activity-contract-check.py

activity-matrix-check:
	python3 ./scripts/sugar-gtk4-activity-matrix-check.py

sugar-modernization-check:
	./scripts/sugar-modernization-check.sh

count-deploy:
	./scripts/count-deploy.sh
