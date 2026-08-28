PROFILE := $(CURDIR)/archiso/aspartame
BUILD_ROOT ?= /media/freezer/SteamLibrary/vms/aspartame-build
OUT_DIR ?= $(BUILD_ROOT)/artifacts/out
WORK_DIR ?= $(BUILD_ROOT)/artifacts/work

.PHONY: iso run rebuild-run clean test

iso:
	./scripts/build-in-arch-root.sh

run:
	ISO=$(OUT_DIR)/aspartame-x86_64.iso ./scripts/run-qemu.sh

rebuild-run: clean iso run

clean:
	./scripts/clean.sh

test:
	./scripts/smoke-test.sh
