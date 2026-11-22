# The design booklet, public edition: the stack today, where it is going, the single points, the failure scenarios, the safety net
# and the reasons, on A3 landscape pages. `make` rebuilds design.pdf.
# Needs a TeX with TikZ (Tectonic: `brew install tectonic`, or MacTeX: make DIAGRAM_TEX=pdflatex).
# Page 2 includes ../diagrams/stack.pdf (the public stack picture), built by that folder's Makefile.
# The PDF must stay under 500 KB (check with ls -l after a build).
DIAGRAM_TEX ?= tectonic -X compile

all: design.pdf

design.pdf: design.tex ../diagrams/stack.pdf
	$(DIAGRAM_TEX) design.tex

../diagrams/stack.pdf: ../diagrams/stack.tex
	$(MAKE) -C ../diagrams stack.pdf

.PHONY: all
