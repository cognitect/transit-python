all : setup.py

setup.py : setup.py.m4
	./bin/make-release

clean :
	rm setup.py
