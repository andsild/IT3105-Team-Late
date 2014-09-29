pdflatex  -interaction=nonstopmode -file-line-error bare_jrnl.tex | grep -A2 -E '*.tex:([0-9]){1,}:' --color=none
