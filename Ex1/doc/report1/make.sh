pdflatex  -interaction=nonstopmode -file-line-error module1.tex | grep -A2 -E '*.tex:([0-9]){1,}:' --color=none
