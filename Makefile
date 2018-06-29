# TESTING

.PHONY: test
test:
	tox

.PHONY: fast-test
# tox requires building the package every time
# takes a long time to compile the rust package in --release mode
fast-test:
	source .tox/py27/bin/activate; \
	py.test -s tests/

.PHONY: fast-test3
fast-test3:
	source .tox/py36/bin/activate; \
	py.test -s tests/

# ALL

.PHONY: clean
clean:
	rm -rf .tox
