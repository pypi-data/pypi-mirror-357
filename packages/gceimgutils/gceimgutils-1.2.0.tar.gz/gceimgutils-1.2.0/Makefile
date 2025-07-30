DESTDIR=
PREFIX=/usr
NAME=gceimgutils
MANPATH=/usr/share/man
dirs = lib man
files = Makefile README.md LICENSE gceremoveimg gcelistimg gcecreateimg gcedeprecateimg gceremoveblob gceuploadblob setup.py requirements-dev.txt requirements.txt

verSpec = $(shell rpm -q --specfile --qf '%{VERSION}' *.spec)
verSrc = $(shell cat lib/gceimgutils/VERSION)

ifneq "$(verSpec)" "$(verSrc)"
$(error "Version mismatch, will not take any action")
endif

clean:
	@find . -name "*.pyc" | xargs rm -f 
	@find . -name "__pycache__" | xargs rm -rf
	@find . -name "*.cache" | xargs rm -rf
	@find . -name "*.egg-info" | xargs rm -rf

pep8: clean
	@pep8 -v --statistics lib/gceimgutils/*
	@pep8 -v --statistics --ignore=E402 tests/*.py

tar: clean
	rm -rf $(NAME)-$(verSrc)
	mkdir $(NAME)-$(verSrc)
	mkdir -p "$(NAME)-$(verSrc)"/man/man1
	cp -r $(dirs) $(files) "$(NAME)-$(verSrc)"
	tar -cjf "$(NAME)-$(verSrc).tar.bz2" "$(NAME)-$(verSrc)"
	rm -rf "$(NAME)-$(verSrc)"

test:
	tox -e unit_py3

install:
	python3 setup.py install --prefix="$(PREFIX)" --root="$(DESTDIR)"
	install -d -m 755 "$(DESTDIR)"/"$(MANDIR)"/man1
	install -m 644 man/man1/* "$(DESTDIR)"/"$(MANDIR)"/man1
	gzip "$(DESTDIR)"/"$(MANDIR)"/man1/gceremoveimg.1

