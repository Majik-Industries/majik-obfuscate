.PHONY: all clean docs dist test lint

VERSION != python3 scripts/inidump.py setup.cfg metadata version
NAME != python3 scripts/inidump.py setup.cfg metadata name
PACKAGE != python3 scripts/inidump.py setup.cfg metadata name | tr - _
AUTHOR != python3 scripts/inidump.py setup.cfg metadata author
WHEEL = $(PACKAGE)-$(VERSION)-py3-none-any.whl
SDIST = $(NAME)-$(VERSION)-tar.gz
DOCTGZ = $(NAME)-doc-$(VERSION).tar.gz

DEPS != find src -type f -name \*.py
DEPS += Makefile

DOCPYPATH=$(PWD)/src/lib

all: dist/$(WHEEL)

docs:  doc/index.rst doc/_build/html/index.html

install: dist/$(WHEEL)

dist: test dist/$(WHEEL) dist/$(DOCTGZ) dist/$(SDIST)

dist/$(DOCTGZ): doc/index.rst doc/_build/html/index.html
	tar -czf dist/$(DOCTGZ) --transform 's,^.,$(NAME),' -C doc/_build/html .


dist/$(WHEEL): $(DEPS)
	@echo "Building wheel: $(@)"
	pip wheel -w dist --use-pep517 --no-deps --isolated .

dist/$(SDIST): $(DEPS)
	@echo "Building sdist: $(@)"
	python3 setup.py sdist

doc/index.rst: doc $(DEPS)
	cd src/lib ; \
	sphinx-apidoc \
		--separate \
		--append-syspath  \
		--full \
		--force \
		--no-headings \
		--module-first \
		--doc-project "$(NAME)" \
		--doc-author "$(AUTHOR)" \
		--doc-version "$(VERSION)" \
		--implicit-namespaces \
		--ext-autodoc \
		--ext-viewcode \
		-o ../../doc majik

doc/_build/html/index.html: doc/index.rst
	cd doc ; make PYTHONPATH="$(DOCPYPATH)" html

test:
	env PATH="$${HOME}/.pyenv/bin:$${HOME}/.pyenv/shims:$${PATH}" \
		PYENV_ROOT="$${HOME}/.pyenv" \
		tox

lint:
	env PATH="$${HOME}/.pyenv/bin:$${HOME}/.pyenv/shims:$${PATH}" \
		PYENV_ROOT="$${HOME}/.pyenv" \
		tox -e linter

doc:
	mkdir -p doc

clean:
	rm -rf dist
	rm -rf doc
	find src -name __pycache__ -exec rm -rf {} +

