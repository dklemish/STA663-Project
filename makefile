.PHONY: all clean

all: make_pictures report.pdf

make_pictures:
	python -m cProfile -o profile_results.txt -s tottime main.py

report.pdf: 
	pdflatex report
	pdflatex report
	pdflatex report

clean:
	rm -f *.aux *.log *.png *.pyc
