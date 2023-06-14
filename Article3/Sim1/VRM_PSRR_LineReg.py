import subprocess
import qspice
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import re

#######
# Plot Default
mpl.rcParams['font.sans-serif'] = ["Arial Rounded MT Bold", 'Arial Unicode MS', 'Arial', 'sans-serif']
mpl.rcParams["mathtext.default"] = "rm"
mpl.rcParams["legend.labelspacing"] = 0.1
mpl.rcParams["legend.columnspacing"] = 0.2
mpl.rcParams["legend.handletextpad"] = 0.3
mpl.rcParams['axes.formatter.useoffset'] = False
mpl.rcParams['xtick.minor.visible'] = True
mpl.rcParams['ytick.minor.visible'] = True
mpl.rcParams['grid.linewidth'] = 1
mpl.rcParams["savefig.dpi"] = 300

plt.style.use('ggplot')
plt.tight_layout()
plt.rc('axes', unicode_minus=False)

#######
# QSPICE
qname = r"c:/Program Files/QSPICE/QSPICE64.exe"
qopt = "-ASCII"

#######
# Generate Transient ".cir" from AC ".cir"
fname = "VRM_PSRR_LineReg"

fAC = fTR = 0
ofile = ""

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

        ofile = ofile + line

        if "AC_begin" in line:
            fAC = 1
        if "TRAN_begin" in line:
            fTR = 1

with open(fname + "_tran.cir", 'w') as f:
    f.write(ofile)

#######
# Run QSPICE of AC for ASCII output

subprocess.run([qname, qopt, fname + ".cir"])

#######
# Plot of AC

q = qspice.Qspice(fname + ".qraw")
q.parse()

val0 = q.get_data('V(vout)',0)
val1 = q.get_data('V(vout)',1)
f=q.get_frequency()

plt.xlabel('Frequency (Hz)', fontsize=14)
plt.ylabel('PSRR (dB)', fontsize=14)

plt.xlim(1,10e6)
plt.ylim(-20,80)
plt.xscale('log')
plt.xticks([1,1e1,1e2,1e3,1e4,1e5,1e6,1e7],["1","10","100","1k","10k","100k","1M","10M"])
#plt.yticks([0,20,40,60,80])
plt.plot(f, 20*np.log10(1/np.absolute(val0)),label="w/o Line-Reg")
plt.plot(f, 20*np.log10(1/np.absolute(val1)),label="w/ Line-Reg")
plt.grid(which='major', linewidth="0.5")
plt.grid(which="minor", linewidth="0.35")
plt.legend(ncol=1, loc="upper right",fancybox=True)

plt.savefig(fname + "_plt.png", format='png', bbox_inches='tight')
plt.show()

#######
# Run QSPICE of Tran for ASCII output

subprocess.run([qname, qopt, fname + "_tran.cir"])

#######
# Plot of Tran

q = qspice.Qspice(fname + "_tran.qraw")
q.parse()

val0 = q.get_data('V(vout)',0)
val1 = q.get_data('V(vout)',1)
t=q.get_time()

fig, (axT, axB) = plt.subplots(2,1,sharex=True,constrained_layout=True)

fig.suptitle("VOUT (V): PSRR by Intentional \"Bad\" Line Regulation")

axB.set_xlabel('Time (s)', fontsize=14)
axB.set_ylabel('w/o Line-Reg', fontsize=14)
axT.set_ylabel('w/  Line-Reg', fontsize=14)

axB.set_ylim(5.02,5.04)
axT.set_ylim(5.07,5.09)

axB.plot(t, val0)
axT.plot(t, val1)

axB.grid(which='major', linewidth="0.5")
axB.grid(which="minor", linewidth="0.35")
axT.grid(which='major', linewidth="0.5")
axT.grid(which="minor", linewidth="0.35")

Bpp = val0.max() - val0.min()
Tpp = val1.max() - val1.min()

axB.text(2, 5.035, "Peak-to-Peak: {0:.2f} mV".format(Bpp*1000))
axT.text(2, 5.085, "Peak-to-Peak: {0:.2f} mV".format(Tpp*1000))

fig.savefig(fname + "_tran_plt.png", format='png', bbox_inches='tight')
plt.show()

