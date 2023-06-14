import re

#######
# Run QSPICE for ASCII output

fname = "VRM_PSRR_LineReg"
fname2 = "VRM_PSRR_LineRegTran"

fAC = 0
fTR = 0
o = ""

with open(fname + ".cir", encoding='SJIS') as f:
    for line in f:
        if "AC_end" in line:
            fAC = 0
        if "TRAN_end" in line:
            fTR = 0

        if fAC == 1:
            line = re.sub("^\\.(.*)$", r"*.\1", line)

        if fTR == 1:
            line = re.sub("^\*(.*)$", r"\1", line)

        o = o + line

        if "AC_begin" in line:
            fAC = 1
        if "TRAN_begin" in line:
            fTR = 1

print(o)

