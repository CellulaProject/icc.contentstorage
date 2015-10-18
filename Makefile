.PHONY: env dev install test edit

LPYTHON=python3
V=$(PWD)/../$(LPYTHON)
PYTHON=$(V)/bin/$(LPYTHON)
ROOT=$(PWD)

env:
	[ -d $(V) ] || virtualenv  $(V)

dev:	env
	$(PYTHON) setup.py develop

install: env
	$(PYTHON) setup.py install
	
edit:	
	cd src && emacs 

test:	
	ip a | grep 2001
	ip a | grep 172.
	. $(V)/bin/activate
	cd src && $(PYTHON) app.py

