.PHONY: all clean

VERSION != python3 scripts/inidump.py setup.cfg metadata version
PACKAGE != python3 scripts/inidump.py setup.cfg metadata name | tr - _
WHEEL = $(PACKAGE)-$(VERSION)-py3-none-any.whl

DEPS != find src -type f -name \*.py


all: dist/$(WHEEL)

install: dist/$(WHEEL)

dist/$(WHEEL): dist $(DEPS)
	@echo "Building wheel: $(@)"
	pip wheel -w dist --use-pep517 --no-deps --isolated .

dist:
	mkdir -p dist

clean:
	rm -rf dist
	find src -name __pycache__ -exec rm -rf {} +

