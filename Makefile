.PHONY: all

all: out/tuffle.html out/tuffle.css

out/tuffle.html: go.py
	./go.py

out/tuffle.css: style.scss
	sass $< $@
