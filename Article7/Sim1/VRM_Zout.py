import PyQSPICE as pqs

import re
import math
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

fname = "VRM_Zout"

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

df = run.LoadQRAW(["V(VOUT)", "I(V1)"])
#print(df)

def CalcImpe(row):
    row["ZO"] = row["V(VOUT)"] / row["I(V1)"]
    row["absZo"] = 20*math.log10(abs(row["ZO"]))
    return row
df = df.apply(CalcImpe, axis=1)

run.comp2real(df, ["Step", "absZo", run.sim['Xlbl']])


#######
# Plot Default

mpl.rcParams.update([['font.sans-serif', ["Arial Rounded MT Bold", 'Arial Unicode MS', 'Arial', 'sans-serif']], ["mathtext.default", "rm"], ["legend.labelspacing", 0.1], ["legend.columnspacing", 0.2], ["legend.handletextpad", 0.3], ['axes.formatter.useoffset', False], ['xtick.minor.visible', True], ['ytick.minor.visible', True], ['grid.linewidth', 1],["savefig.dpi", 300], ["axes.unicode_minus", False]])

#######
# Plotting Pandas, AC

plt.close('all')

plt.style.use('ggplot')

fig, ax = plt.subplots(tight_layout=True)
#fig.suptitle("$Z_{OUT}$")

df[df.Step == 0].plot(ax=ax, x="Freq",  y="absZo", label="Open Loop")
df[df.Step == 1].plot(ax=ax, x="Freq",  y="absZo", label="Closed Loop")

ax.set_xscale('log')
ax.set_xlim(1,10e6)
ax.set_ylim(-60,80)
ax.set_xticks([1,1e1,1e2,1e3,1e4,1e5,1e6,1e7],["1","10","100","1k","10k","100k","1M","10M"])
ax.set_yticks([-60,-40,-20,0,20,40,60,80],["1m","10m","100m","1","10","100","1k","10k"])
ax.set_ylabel('Output Impedance ($\Omega$)', fontsize=14)
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

df2 = run2.LoadQRAW(["V(VOUT)"])

#######
# Plotting Pandas, Tran

plt.close('all')

plt.style.use('ggplot')

fig2, (axL, axR) = plt.subplots(1,2,sharey=True,constrained_layout=True)
#fig.suptitle("$Z_{OUT}$")

df2[df2.Step == 0].plot(ax=axL, x="Time",  y="V(VOUT)", label="Open Loop")
df2[df2.Step == 1].plot(ax=axR, x="Time",  y="V(VOUT)", label="Closed Loop")

fig2.suptitle("$V_{OUT}$ Ripple from 10mA Current Ripple")

axL.set_xlabel('Open Loop:  Time ($\mu$s)', fontsize=14)
axR.set_xlabel('Closed Loop:  Time R ($\mu$s)', fontsize=14)
axL.set_ylabel('$V_{OUT} (V)$', fontsize=14)

axL.set_ylim(5.029,5.033)
axR.set_ylim(5.029,5.033)

axL.grid(which='major', linewidth="0.5")
axL.grid(which="minor", linewidth="0.35")
axR.grid(which='major', linewidth="0.5")
axR.grid(which="minor", linewidth="0.35")

Lpp = (df2[df2.Step == 0])["V(VOUT)"].max() - (df2[df2.Step == 0])["V(VOUT)"].min()
Rpp = (df2[df2.Step == 1])["V(VOUT)"].max() - (df2[df2.Step == 1])["V(VOUT)"].min()

axL.set_xticks([0,20e-6,40e-6,60e-6,80e-6,100e-6,120e-6,140e-6,160e-6,180e-6,200e-6],["0","20","40","60","80","100","120","140","160","180","200"])
axR.set_xticks([0,20e-6,40e-6,60e-6,80e-6,100e-6,120e-6,140e-6,160e-6,180e-6,200e-6],["0","20","40","60","80","100","120","140","160","180","200"])

axL.text(20e-6, 5.0295, "Peak-to-Peak: {0:.2f} mV".format(Lpp*1000))
axR.text(20e-6, 5.0295, "Peak-to-Peak: {0:.2f} mV".format(Rpp*1000))

axL.legend(ncol=1, loc="lower center",fancybox=True)
axR.legend(ncol=1, loc="lower center",fancybox=True)

plt.savefig(ftran + "_plt.png", format='png', bbox_inches='tight')
plt.show()

plt.close('all')

