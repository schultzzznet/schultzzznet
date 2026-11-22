# The stack picture and the progress picture, drawn in TikZ. `make` rebuilds the PDFs (for zooming and printing) and the PNGs the pages show.
# Needs a TeX with TikZ (Tectonic: `brew install tectonic`, or MacTeX: make DIAGRAM_TEX=pdflatex) and Poppler (`brew install poppler`).
# The PNGs are 125 dpi so they stay under 500 KB.
#
# progress.png's numbers are in progress-data.tex, which ../../../scripts/build-progress.py writes from docs/_data/progress.yml
# (standard library Python only). The PNG gets the data digest of the PDF it was made from, so the guard can tell a stale picture.
DIAGRAM_TEX ?= tectonic -X compile
PYTHON ?= python3
ROOT := ../../..

all: stack.pdf stack.png progress.png

%.pdf: %.tex
	$(DIAGRAM_TEX) $<

%.png: %.pdf
	pdftocairo -png -r 125 -singlefile $< $*

progress-data.tex: $(ROOT)/docs/_data/progress.yml $(ROOT)/scripts/build-progress.py
	cd $(ROOT) && $(PYTHON) scripts/build-progress.py

progress.pdf: progress.tex progress-data.tex
	$(DIAGRAM_TEX) progress.tex

progress.png: progress.pdf
	pdftocairo -png -r 125 -singlefile progress.pdf progress
	$(PYTHON) $(ROOT)/scripts/build-progress.py --stamp-png progress.png progress.pdf

.PHONY: all
