import PyQSPICE as pqs

import re
import math
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

fname = "VRM_PSRR_OnOff"

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

df[df.Step == 0].plot(ax=ax, x="Freq",  y="PSRR", label="LDO OFF")
df[df.Step == 1].plot(ax=ax, x="Freq",  y="PSRR", label="LDO ON")

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


