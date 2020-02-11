TARGETPY = $(filter-out setup.py,$(wildcard *.py))
TARGETS = $(TARGETPY:.py=)

all:	$(TARGETS:=.built)

%.built:	%/Dockerfile
	docker build -t $* $*

%/Dockerfile:	%.py
	python3 -m iisysgen.cmd generate \
	    $(addprefix -c ,$(wildcard $*.yaml) $(wildcard $*.json)) \
	    $*

# Depend on any configuration files
define cfg_template =
$(1)/Dockerfile:	$(wildcard $(1).yaml) $(wildcard $(1).json)
endef

$(foreach t,$(TARGETS),$(eval $(call cfg_template,$(t))))

$(addsuffix /Dockerfile,$(TARGETS)):	iisysgen/docker.py

.PRECIOUS:	%/Dockerfile
