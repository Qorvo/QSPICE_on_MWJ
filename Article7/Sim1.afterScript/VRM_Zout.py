from PyQSPICE import clsQSPICE as pqs

import math
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

import re

fname = "VRM_Zout"

run = pqs(fname)

run.InitPlot()

run.qsch2cir()
run.cir2qraw()

run.setNline(199)

zex = 'V(VOUT)/I(V1)'
df = (run.LoadQRAW([zex])).rename(columns = {zex: "Zout"})

df = run.GainPhase(df, "Zout", "absZo", "argZo")

run.comp2real(df, ["Step", "absZo", "argZo", run.sim['Xlbl']])

#######
# Plotting Pandas, AC

plt.close('all')

fig, ax = plt.subplots(tight_layout=True)
#fig.suptitle("$Z_{OUT}$")

df[df.Step == 0].plot(ax=ax, x="Freq",  y="absZo", label="Open Loop")
df[df.Step == 1].plot(ax=ax, x="Freq",  y="absZo", label="Closed Loop")
run.PrepFreqImpePlot(ax, "Frequency (Hz)", r"Output Impedance ($\Omega$)", [1,10e6], "auto")

plt.savefig(run.path['base'] + "_plt.png", format='png', bbox_inches='tight')
plt.show()

plt.close('all')

#######
# Generate Transient ".cir" from AC ".cir"

fAC = fTR = 0
ofile = ""

with open(fname + ".cir", encoding='SJIS') as f:
    for line in f:
        if "AC_end" in line: fAC = 0
        if "TRAN_end" in line: fTR = 0

        if fAC == 1: line = re.sub(r"^\.(.*)$", r"*.\1", line)
        if fTR == 1: line = re.sub(r"^\*(.*)$", r"\1", line)

        ofile = ofile + line

        if "AC_begin" in line: fAC = 1
        if "TRAN_begin" in line: fTR = 1

ftran = fname + "_tran"

with open(ftran + ".cir", 'w') as f:
    f.write(ofile)

run2 = pqs(ftran)

run2.cir2qraw()

run2.setNline(199)

df2 = run2.LoadQRAW(["V(VOUT)"])

#######
# Plotting Pandas, Tran

plt.close('all')

fig2, (axL, axR) = plt.subplots(1,2,sharey=True,constrained_layout=True)
#fig.suptitle("$Z_{OUT}$")

df2[df2.Step == 0].plot(ax=axL, x="Time",  y="V(VOUT)", label="Open Loop")
df2[df2.Step == 1].plot(ax=axR, x="Time",  y="V(VOUT)", label="Closed Loop")

fig2.suptitle("$V_{OUT}$ Ripple from 10mA Current Ripple")

run.PrepTimePlot(axL, r"Open Loop:  Time", r"$V_{OUT} (V)$", [0,200e-6], [5.029,5.033])
run.PrepTimePlot(axR, r"Closed Loop:Time", r"$V_{OUT} (V)$", [0,200e-6], [5.029,5.033])

Lpp = (df2[df2.Step == 0])["V(VOUT)"].max() - (df2[df2.Step == 0])["V(VOUT)"].min()
Rpp = (df2[df2.Step == 1])["V(VOUT)"].max() - (df2[df2.Step == 1])["V(VOUT)"].min()

axL.text(20e-6, 5.0295, "Peak-to-Peak: {0:.2f} mV".format(Lpp*1000))
axR.text(20e-6, 5.0295, "Peak-to-Peak: {0:.2f} mV".format(Rpp*1000))

axL.legend(ncol=1, loc="lower center",fancybox=True)
axR.legend(ncol=1, loc="lower center",fancybox=True)

plt.savefig(ftran + "_plt.png", format='png', bbox_inches='tight')
plt.show()

plt.close('all')

