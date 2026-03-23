import sys
import re

colors = {
    "31": "termred",
    "32": "termgreen",
    "36": "termcyan",
}

ansi = re.compile(r"\x1b\[([0-9;]+)m")

open_color = None

for line in sys.stdin:
    pos = 0
    out = ""
    
    for m in ansi.finditer(line):
        out += line[pos:m.start()]
        codes = m.group(1).split(";")

        if "0" in codes:
            if open_color:
                out += "}"
                open_color = None

        for c in codes:
            if c in colors:
                if open_color:
                    out += "}"
                out += "\\textcolor{%s}{" % colors[c]
                open_color = colors[c]

        pos = m.end()

    out += line[pos:]
    print(out, end="")

if open_color:
    print("}")