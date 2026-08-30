PROFILE := $(CURDIR)/archiso/aspartame
BUILD_ROOT ?= /media/freezer/SteamLibrary/vms/aspartame-build
OUT_DIR ?= $(BUILD_ROOT)/artifacts/out
WORK_DIR ?= $(BUILD_ROOT)/artifacts/work

.PHONY: iso run rebuild-run clean test sugar-info sugar-reload sugar-session-restart sugar-logs sugar-screenshot sugar-visual-check sugar-patch-check sugar-open-control-panel count-deploy

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

count-deploy:
	./scripts/count-deploy.sh
