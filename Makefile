PROFILE := $(CURDIR)/archiso/aspartame
OUT_DIR ?= $(CURDIR)/out
WORK_DIR ?= $(CURDIR)/work

.PHONY: iso run rebuild-run clean test

iso:
	PROFILE=$(PROFILE) OUT_DIR=$(OUT_DIR) WORK_DIR=$(WORK_DIR) ./scripts/build-iso.sh

run:
	ISO=$(OUT_DIR)/aspartame-x86_64.iso ./scripts/run-qemu.sh

rebuild-run: clean iso run

clean:
	./scripts/clean.sh

test:
	./scripts/smoke-test.sh

