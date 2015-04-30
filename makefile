report.pdf: report.tex clusters.png
	pdflatex report
	pdflatex report
	pdflatex report

clusters.png: 
	python main.py

.PHONY: all clean

all: report.pdf

clean:
	rm -f *.aux *.log *.png
