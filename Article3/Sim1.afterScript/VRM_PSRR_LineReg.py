import PyQSPICE as pqs

import re
import math
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

fname = "VRM_PSRR_LineReg"

run = pqs.PyQSPICE(fname)
#print(run.path)
#print(run.gpath)
#print(run.ts)
#print(run.date)

#print(run.date['cir'])
run.qsch2cir()
#print(run.date['cir'])

#print(run.date['qraw'])
run.cir2qraw()
#print(run.date['qraw'])

run.setNline(199)

df = run.LoadQRAW(["V(vout)"])
#print(df)

def CalcGain(row):
    row["PSRR"] = 20*math.log10(1/abs(row["V(vout)"]))
    return row
df = df.apply(CalcGain, axis=1)

run.comp2real(df, ["Step", "PSRR", run.sim['Xlbl']])


#######
# Plot Default

mpl.rcParams.update([['font.sans-serif', ["Arial Rounded MT Bold", 'Arial Unicode MS', 'Arial', 'sans-serif']], ["mathtext.default", "rm"], ["legend.labelspacing", 0.1], ["legend.columnspacing", 0.2], ["legend.handletextpad", 0.3], ['axes.formatter.useoffset', False], ['xtick.minor.visible', True], ['ytick.minor.visible', True], ['grid.linewidth', 1],["savefig.dpi", 300], ["axes.unicode_minus", False]])

#######
# Plotting Pandas, AC

plt.close('all')

plt.style.use('ggplot')

fig, ax = plt.subplots(tight_layout=True)
#fig.suptitle("$Z_{OUT}$")

df[df.Step == 0].plot(ax=ax, x="Freq",  y="PSRR", label="w/o Line-Reg")
df[df.Step == 1].plot(ax=ax, x="Freq",  y="PSRR", label="w/ Line-Reg")

ax.set_xscale('log')
ax.set_xlim(1,10e6)
ax.set_ylim(-20,80)
ax.set_xticks([1,1e1,1e2,1e3,1e4,1e5,1e6,1e7],["1","10","100","1k","10k","100k","1M","10M"])
ax.set_ylabel('PSRR (dB)', fontsize=14)
ax.set_xlabel('Frequency (Hz)', fontsize=14)
ax.minorticks_on()
ax.xaxis.set_major_locator(mpl.ticker.LogLocator(numticks=13))
ax.xaxis.set_minor_locator(mpl.ticker.LogLocator(numticks=13, subs=(.2,.4,.6,.8)))

ax.grid(which='major', linewidth="0.5")
ax.grid(which='minor', linewidth="0.35")

plt.legend(ncol=1, loc="upper right",fancybox=True)

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

        if fAC == 1: line = re.sub("^\\.(.*)$", r"*.\1", line)
        if fTR == 1: line = re.sub("^\*(.*)$", r"\1", line)

        ofile = ofile + line

        if "AC_begin" in line: fAC = 1
        if "TRAN_begin" in line: fTR = 1

ftran = fname + "_tran"

with open(ftran + ".cir", 'w') as f:
    f.write(ofile)

run2 = pqs.PyQSPICE(ftran)
#print(run2.path)
#print(run2.gpath)
#print(run2.ts)
#print(run2.date)

#print(run.date['qraw'])
run2.cir2qraw()
#print(run.date['qraw'])

run2.setNline(199)

df2 = run2.LoadQRAW(["V(vout)"])

#######
# Plotting Pandas, Tran

plt.close('all')

plt.style.use('ggplot')

fig2, (axT, axB) = plt.subplots(2,1,sharex=True,constrained_layout=True)

df2[df2.Step == 0].plot(ax=axB, x="Time",  y="V(vout)", label="w/o Line-Reg")
df2[df2.Step == 1].plot(ax=axT, x="Time",  y="V(vout)", label="w Line-Reg")

fig2.suptitle("VOUT (V): PSRR by Intentional \"Bad\" Line Regulation")

axB.set_xlabel('Time (s)', fontsize=14)
axB.set_ylabel('w/o Line-Reg', fontsize=14)
axT.set_ylabel('w/ Line-Reg', fontsize=14)

axB.set_ylim(5.02,5.04)
axT.set_ylim(5.07,5.09)

axB.grid(which='major', linewidth="0.5")
axB.grid(which="minor", linewidth="0.35")
axT.grid(which='major', linewidth="0.5")
axT.grid(which="minor", linewidth="0.35")

Bpp = (df2[df2.Step == 0])["V(vout)"].max() - (df2[df2.Step == 0])["V(vout)"].min()
Tpp = (df2[df2.Step == 1])["V(vout)"].max() - (df2[df2.Step == 1])["V(vout)"].min()

axB.text(2, 5.035, "Peak-to-Peak: {0:.2f} mV".format(Bpp*1000))
axT.text(2, 5.085, "Peak-to-Peak: {0:.2f} mV".format(Tpp*1000))

plt.savefig(ftran + "_plt.png", format='png', bbox_inches='tight')
plt.show()

plt.close('all')

