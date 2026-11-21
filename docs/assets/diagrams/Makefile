# The stack picture, drawn in TikZ. `make` rebuilds the PDF (for zooming and printing) and the PNG the page shows.
# Needs a TeX with TikZ (Tectonic: `brew install tectonic`, or MacTeX: make DIAGRAM_TEX=pdflatex) and Poppler (`brew install poppler`).
# The PNG is 125 dpi so it stays under 500 KB.
DIAGRAM_TEX ?= tectonic -X compile

all: stack.pdf stack.png

%.pdf: %.tex
	$(DIAGRAM_TEX) $<

%.png: %.pdf
	pdftocairo -png -r 125 -singlefile $< $*

.PHONY: all
