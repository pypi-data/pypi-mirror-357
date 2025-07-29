.PHONY: install
ifeq ($(OS),Windows_NT)
  EXE=.exe
  MINI=mini/
endif

perl5-$(project_version)/perl$(EXE): perl5-$(project_version)/$(MINI)config.h
ifneq ($(OS),Windows_NT)
	$(MAKE) -j$(shell nproc) -C perl5-$(project_version)
endif

install: perl5-$(project_version)/perl$(EXE)
ifeq ($(OS),Windows_NT)
	cd perl5-$(project_version)/win32 && LC_ALL=C LANG=C mingw32-make -j$(shell nproc) -f GNUMakefile PLMAKE=mingw32-make INST_TOP=$(project_root)\\$(prefixdir) INST_HTML=$(project_root)\\$(prefixdir)\\share\\doc\\HTML\\en\\perl5 install
else
	DESTDIR=$(prefix) $(MAKE) -j$(shell nproc) -C perl5-$(project_version) install
endif
	rm -rf perl5-$(project_version)/$(MINI)config.h

perl5-$(project_version)/$(MINI)config.h: perl5-$(project_version)/Configure
ifeq ($(OS),Windows_NT)
	cd perl5-$(project_version)/win32 && LC_ALL=C LANG=C mingw32-make -j$(shell nproc) -f GNUMakefile PLMAKE=mingw32-make CCHOME=$(MINGW_PREFIX) INST_TOP=$(project_root)\\$(prefixdir)
else
	cd perl5-$(project_version) && ../$^ -des -Dusedevel -Dprefix=/ -Dsiteprefix=/ -Dprivlib=/share/perl5/core_perl -Darchlib=/lib/perl5/$(project_version)/core_perl -Dsitelib=/share/perl5/site_perl -Dsitearch=/usr/lib/perl5/$(project_version)/site_perl -Dscriptdir=/bin -Dsitescript=/bin -Dman1ext=1 -Dman3ext=3 -Dversiononly=no
endif

perl5-$(project_version)/Configure: v$(project_version).tar.gz
	tar xzf $<

v$(project_version).tar.gz:
	curl -LO https://github.com/Perl/perl5/archive/refs/tags/$@
