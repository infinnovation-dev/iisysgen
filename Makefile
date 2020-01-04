TARGETPY = $(filter-out iisysgen.py, $(wildcard *.py))
TARGETS = $(TARGETPY:.py=)

all:	$(TARGETS:=.built)

%.built:	%/Dockerfile
	docker build -t $* $*

%/Dockerfile:	%.py
	python3 -m iisysgen build -c $*.yaml $*

$(addsuffix /Dockerfile,$(TARGETS)):	%/Dockerfile:	%.yaml

$(addsuffix /Dockerfile,$(TARGETS)):	iisysgen.py

.PRECIOUS:	%/Dockerfile
