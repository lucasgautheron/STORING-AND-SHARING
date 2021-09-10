all: main.pdf

# This rule is executed last, and renders the full PDF from the manuscript with latexmk.
# The -g flag is used to *always* process the document, even if no changes have been made to it.

main.pdf: main.tex references.bib Fig4.pdf Fig5.pdf
	latexmk -pdf -g $<

Fig4.pdf: code/recall.py scores.csv
	code/recall.py vandam-data

Fig5.pdf: code/confusion_matrix.py vandam-data/annotations/eaf/converted/*.csv vandam-data/annotations/vtc/converted/*.csv
	code/confusion_matrix.py vandam-data

scores.csv: vandam-data/annotations/its/converted/*.csv vandam-data/annotations/vtc/converted/*.csv vandam-data/annotations/eaf/converted/*.csv vandam-data/annotations/cha/aligned/converted/*.csv
	code/recall.py vandam-data

vandam-data/annotations/its/converted/*.csv:
	datalad get vandam-data/annotations/its/converted

vandam-data/annotations/vtc/converted/*.csv:
	datalad get vandam-data/annotations/vtc/converted

vandam-data/annotations/cha/aligned/converted/*.csv:
	datalad get vandam-data/annotations/cha/aligned/converted

vandam-data/annotations/eaf/converted/*.csv:
	datalad get vandam-data/annotations/eaf/converted

sample.pdf: code/sample.py vandam-data/recordings/converted/standard
	python code/sample.py

vandam-data/recordings/converted/standard:
	datalad get vandam-data/recordings/converted/standard

# This rule cleans up temporary LaTeX files, and result and PDF files
clean:
	rm -f main.bbl main.aux main.blg main.log main.out main.pdf main.tdo main.fls main.fdb_latexmk texput.log *-eps-converted-to.pdf scores.csv
	datalad drop vandam-data/annotations/its/converted
	datalad drop vandam-data/annotations/vtc/converted
	datalad drop vandam-data/recordings/converted/standard
