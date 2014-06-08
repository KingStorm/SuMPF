install:
	# installs the python module for SuMPF on the system.
	cd source && python setup.py install && rm -r build

install_user:
	# installs the python module for SuMPF for the current user.
	# The module will most likely be somewhere in ~/.local/lib/python...
	cd source && python setup.py install --user && rm -r build

clean:
	# deletes the python bytecode by removing the *.pyc files and __pycache__
	# directories from the source, the test and the tools directories.
	rm -vf `find -name *.pyc`
	rm -vrf `find -name __pycache__`

mrproper:	clean
	# deletes the Python bytecode just like "make clean", but also deletes the
	# automatically generated documentation.
	rm -rf documentation/doxygen
	rm -rf documentation/moduledoc
	rm -f documentation/statistics.htm

test_quick:
	# runs the quick standard tests of SuMPF's test suite with the default
	# Python interpreter.
	cd tests && python run_tests.py

test:
	# runs SuMPF's test suite with the default Python interpreter. This run
	# includes tests that write to disk and tests that take a longer time to run.
	# It skips gui tests, time variant tests and interactive tests.
	cd tests && python run_tests.py -w -l

test3:
	# runs SuMPF's test suite with the Python3 interpreter. This run includes
	# tests that write to disk and tests that take a longer time to run. It skips
	# gui tests, time variant tests and interactive tests.
	cd tests && python3 run_tests.py -w -l

test_pypy:
	# runs SuMPF's test suite with the PyPy interpreter. This run includes tests
	# that write to disk and tests that take a longer time to run. It skips gui
	# tests, time variant tests and interactive tests.
	cd tests && pypy run_tests.py -w -l

test_all:
	# runs SuMPF's full test suite with all interpreters that are installed and
	# supported by SuMPF. This starts with running all tests except for the
	# incomplete ones with the standard python interpreter. After that all tests
	# except for the incomplete, the interactive and the gui tests are run twice
	# with each installed and supported interpreter (the standard one (most
	# likely Python2), Python3 and PyPy).
	cd tests && python run_tests.py -w -g -l -t -i
	cd tests && python run_tests.py -w -l -t -r 2
	if which python3 > /dev/null; then cd tests && python3 run_tests.py -w -l -t -r 2; fi
	if which pypy > /dev/null; then cd tests && pypy run_tests.py -w -l -t -r 2; fi

doc:
	# creates the documentation files that are created automatically.
	# The files can be found in the ./documentation folder
	doxygen tools/Doxyfile
	export PYTHONPATH="$$PYTHONPATH":"`pwd`/source" && python tools/moduledoc.py -o documentation/moduledoc/ -d documentation/doxygen/html/ -m sumpf -s documentation/header.js
	python tools/statistics.py -f documentation/statistics.htm

install_examples:
	# installs the examples of SuMPF as executable programs on the system.
	# The programs can be run with the command sumpf_NAME, where NAME is the
	# name of the example function.
	# SuMPF needs to be installed before this make target can be run.
	python tools/installexamples.py -o /usr/bin/bin

install_examples_local:
	# installs the examples of SuMPF as executable programs in ./bin.
	# SuMPF needs to be installed before this make target can be run.
	python tools/installexamples.py -o ./bin

