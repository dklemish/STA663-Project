.PHONY: all

all: make_pictures report.pdf clean

make_pictures:
	python main.py
#	python -m cProfile -o profile_results.txt -s tottime main.py

report.pdf: 
	pdflatex report
	pdflatex report
	pdflatex report

clean:
	rm -f *aux *log *png
