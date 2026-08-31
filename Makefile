PROFILE := $(CURDIR)/archiso/aspartame
BUILD_ROOT ?= /media/freezer/SteamLibrary/vms/aspartame-build
OUT_DIR ?= $(BUILD_ROOT)/artifacts/out
WORK_DIR ?= $(BUILD_ROOT)/artifacts/work

.PHONY: iso run rebuild-run clean test sugar-info sugar-reload sugar-session-restart sugar-logs sugar-screenshot sugar-visual-check sugar-patch-check sugar-open-control-panel sugar-upstream-sync sugar-gtk4-init sugar-gtk4-build sugar-gtk4-run sugar-gtk4-smoke sugar-gtk4-check sugar-gtk4-update sugar-modernization-check count-deploy

iso:
	./scripts/build-in-arch-root.sh

run:
	./scripts/run-qemu.sh

rebuild-run: clean iso run

clean:
	./scripts/clean.sh

test:
	./scripts/smoke-test.sh

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

sugar-modernization-check:
	./scripts/sugar-modernization-check.sh

count-deploy:
	./scripts/count-deploy.sh
