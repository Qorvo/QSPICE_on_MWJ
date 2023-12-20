from PyQSPICE import clsQSPICE as pqs

import subprocess
import re
import math
import cmath
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from numpy import sin, cos, pi, linspace

fname = "VRM_ZoPart8"

run = pqs(fname)

run.qsch2cir()
run.cir2qraw()

run.setNline(2048)

g = "V(VOUT)/V(VO)"
z = "V(VOUT)"

df0 = run.LoadQRAW([g, z])

############################################

df = df0[df0.Step <= 1].reset_index(drop=True)
df = run.GainPhase(df, g, "gain", "phase", "reGain", "imGain", -1)

df["Zout(Closed)"] = df0.query('Step == 2 or Step == 3').reset_index(drop=True).loc[:,"V(VOUT)"]
df["Zout(Open)"] = df0.query('Step == 4 or Step == 5').reset_index(drop=True).loc[:,"V(VOUT)"]

#df = run.Zout(df, "Zout(Open)", "Zout(closed)", "T(s)")
def CalcZ(row):
    row["T"] = 1 - row["Zout(Open)"] / row["Zout(Closed)"]
    return row
df = df.apply(CalcZ, axis=1)

df = run.GainPhase(df, "T", "abs(Tzo)", "arg(Tzo)")
df = run.GainPhase(df, "Zout(Closed)", "abs(Zoc)", "arg(Zoc)")
df = run.GainPhase(df, "Zout(Open)", "abs(Zoo)", "arg(Zoo)")
run.comp2real(df, ["Step", "reGain", "imGain", "gain", "phase", "abs(Tzo)", "arg(Tzo)", "abs(Zoc)", "arg(Zoc)", "abs(Zoo)", "arg(Zoo)", run.sim['Xlbl']])

############################################

# Plot Default

mpl.rcParams.update([['font.sans-serif', ["Arial Rounded MT Bold", 'Arial Unicode MS', 'Arial', 'sans-serif']], ["mathtext.default", "rm"], ["legend.labelspacing", 0.1], ["legend.columnspacing", 0.2], ["legend.handletextpad", 0.3], ['axes.formatter.useoffset', False], ['xtick.minor.visible', True], ['ytick.minor.visible', True], ['grid.linewidth', 1],["savefig.dpi", 300], ["axes.unicode_minus", False]])
plt.close('all')
plt.style.use('ggplot')

############################################

# Prepare a blank plotting area
fig, ax = plt.subplots(2,3,sharex=True,constrained_layout=True,figsize=(12,6))

# Bode Plots
# Position: Upper Left [0,0]
df[df.Step == 0].plot(ax=ax[0,0], x="Freq",  y="gain", label="Loop #0")
df[df.Step == 1].plot(ax=ax[0,0], x="Freq",  y="gain", label="Loop #1")

ax[0,0].set_title('Bode Plot', fontsize=14)
ax[0,0].set_xscale('log')
ax[0,0].set_ylabel('Gain (dB)', fontsize=14)
ax[0,0].set_ylim([-120,120])
ax[0,0].grid(which='major', linewidth="0.5")
ax[0,0].grid(which="minor", linewidth="0.35")
ax[0,0].minorticks_on()

# Bode Plots
# Position: Lower Left [1,0]
df[df.Step == 0].plot(ax=ax[1,0], x="Freq",  y="phase", label="Loop #0")
df[df.Step == 1].plot(ax=ax[1,0], x="Freq",  y="phase", label="Loop #1")

ax[1,0].set_ylabel('Phase (°)', fontsize=14)
ax[1,0].set_xlabel('Frequency (Hz)', fontsize=14)
ax[1,0].set_ylim([-30, 180])
ax[1,0].grid(which='major', linewidth="0.5")
ax[1,0].grid(which="minor", linewidth="0.35")
ax[1,0].minorticks_on()

# Output-Impedance, Closed-Loop
# Position: Upper Center [0,1]
df[df.Step == 0].plot(ax=ax[0,1], x="Freq",  y="abs(Zoc)", label="Loop #0")
df[df.Step == 1].plot(ax=ax[0,1], x="Freq",  y="abs(Zoc)", label="Loop #1")

ax[0,1].set_title('Output Impedance, Closed-Loop', fontsize=14)
ax[0,1].set_xscale('log')
ax[0,1].set_ylim([-80,60])
ax[0,1].set_ylabel(r'$Z_{OUT}$(Close) (dB $\Omega$)', fontsize=14)
ax[0,1].grid(which='major', linewidth="0.5")
ax[0,1].grid(which="minor", linewidth="0.35")
ax[0,1].minorticks_on()

# Position: Lower Center [1,1]
df[df.Step == 0].plot(ax=ax[1,1], x="Freq",  y="arg(Zoc)", label="Loop #0")
df[df.Step == 1].plot(ax=ax[1,1], x="Freq",  y="arg(Zoc)", label="Loop #1")

ax[1,1].set_ylabel('Phase (°)', fontsize=14)
ax[1,1].set_xlabel('Frequency (Hz)', fontsize=14)
ax[1,1].set_ylim([-90,90])
ax[1,1].grid(which='major', linewidth="0.5")
ax[1,1].grid(which="minor", linewidth="0.35")
ax[1,1].minorticks_on()

# Output-Impedance, Open-Loop
# Position: Upper Right [0,2]
df[df.Step == 0].plot(ax=ax[0,2], x="Freq",  y="abs(Zoo)", label="Loop #0")
df[df.Step == 1].plot(ax=ax[0,2], x="Freq",  y="abs(Zoo)", label="Loop #1")

ax[0,2].set_title('Output Impedance, Open-Loop', fontsize=14)
ax[0,2].set_xscale('log')
ax[0,2].set_ylim([-80,60])
ax[0,2].set_ylabel(r'$Z_{OUT}$(Open) (dB $\Omega$)', fontsize=14)
ax[0,2].grid(which='major', linewidth="0.5")
ax[0,2].grid(which="minor", linewidth="0.35")
ax[0,2].minorticks_on()

# Output-Impedance, Open-Loop
# Position: Lower Right [1,2]
df[df.Step == 0].plot(ax=ax[1,2], x="Freq",  y="arg(Zoo)", label="Loop #0")
df[df.Step == 1].plot(ax=ax[1,2], x="Freq",  y="arg(Zoo)", label="Loop #1")

ax[1,2].set_ylabel('Phase (°)', fontsize=14)
ax[1,2].set_xlabel('Frequency (Hz)', fontsize=14)
ax[1,2].set_ylim([-90,90])
ax[1,2].grid(which='major', linewidth="0.5")
ax[1,2].grid(which="minor", linewidth="0.35")
ax[1,2].minorticks_on()

run.tstime(['png'])
plt.savefig(run.path['png'], format='png', bbox_inches='tight')

plt.show()
plt.close('all')

############################################

# Prepare a blank plotting area
fig, ax = plt.subplots(2,2,sharex=True,constrained_layout=True,figsize=(12,6))

for i in [0, 1]:
    df[df.Step == i].plot(ax=ax[0,i], x="Freq",  y="gain", label="Bode Plot")
    df[df.Step == i].plot(ax=ax[0,i], x="Freq",  y="abs(Tzo)", label="Zout Reconstruction", linestyle="dotted", linewidth=3)

    ax[0,i].set_title(f'Loop #{i}', fontsize=14)
    ax[0,i].set_xscale('log')
    ax[0,i].set_ylabel('Gain (dB)', fontsize=14)
    ax[0,i].set_ylim([-120,120])
    ax[0,i].grid(which='major', linewidth="0.5")
    ax[0,i].grid(which="minor", linewidth="0.35")
    ax[0,i].minorticks_on()

    df[df.Step == i].plot(ax=ax[1,i], x="Freq",  y="phase", label="Bode Plot")
    df[df.Step == i].plot(ax=ax[1,i], x="Freq",  y="arg(Tzo)", label="Zout Reconstruction", linestyle="dotted", linewidth=3)

    ax[1,i].set_ylabel('Phase (°)', fontsize=14)
    ax[1,i].set_xlabel('Frequency (Hz)', fontsize=14)
    ax[1,i].set_ylim([-30,180])
    ax[1,i].grid(which='major', linewidth="0.5")
    ax[1,i].grid(which="minor", linewidth="0.35")
    ax[1,i].minorticks_on()

plt.savefig("PltTs0.png", format='png', bbox_inches='tight')

plt.show()
plt.close('all')

############################################

# Prepare a blank plotting area
fig, ax = plt.subplots(2,2,sharex=True,constrained_layout=True,figsize=(12,6))

ax[0,0].set_title('Bode Plot', fontsize=14)
ax[0,1].set_title('Zout Reconstruction', fontsize=14)

for i in [0, 1]:
    df[df.Step == i].plot(ax=ax[0,0], x="Freq",  y="gain", label=f"Loop {i}")
    df[df.Step == i].plot(ax=ax[0,1], x="Freq",  y="abs(Tzo)", label=f"Loop {i}")


    ax[0,i].set_xscale('log')
    ax[0,i].set_ylabel('Gain (dB)', fontsize=14)
    ax[0,i].set_ylim([-120,120])
    ax[0,i].grid(which='major', linewidth="0.5")
    ax[0,i].grid(which="minor", linewidth="0.35")
    ax[0,i].minorticks_on()

    df[df.Step == i].plot(ax=ax[1,0], x="Freq",  y="phase", label=f"loop {i}")
    df[df.Step == i].plot(ax=ax[1,1], x="Freq",  y="arg(Tzo)", label=f"loop {i}")

    ax[1,i].set_ylabel('Phase (°)', fontsize=14)
    ax[1,i].set_xlabel('Frequency (Hz)', fontsize=14)
    ax[1,i].set_ylim([-30,180])
    ax[1,i].grid(which='major', linewidth="0.5")
    ax[1,i].grid(which="minor", linewidth="0.35")
    ax[1,i].minorticks_on()

plt.savefig("PltTs1.png", format='png', bbox_inches='tight')

plt.show()
plt.close('all')

############################################

df00 = df.loc[:,["Step","Freq","abs(Zoo)"]].rename(columns = {"abs(Zoo)": "dZo"}) - df.loc[:,["Step","Freq","abs(Zoc)"]].rename(columns={"abs(Zoc)": "dZo"})
#print(df.loc[:,["abs(Zoo)"]].rename(columns = {"abs(Zoo)": "a"}))
#print(df[df.Step == 0].loc[:,["abs(Zoc)"]].rename(columns={"abs(Zoc)": "a"})
df00["Freq"] = df.loc[:,"Freq"]
df00["Step"] = df.loc[:,"Step"]
# Prepare a blank plotting area
fig, ax = plt.subplots(2,2,sharex=True,constrained_layout=True,figsize=(12,6))

for i in [0, 1]:
#if 0:
    df[df.Step == i].plot(ax=ax[0,i], x="Freq",  y="gain", label="Bode Plot")
    df00[df00.Step == i].plot(ax=ax[0,i], x="Freq",  y="dZo", label=r"|$Z_{O,Open}$| - |$Z_{O,Close}$|", linestyle="dotted", linewidth=3)

    ax[0,i].set_title(f'Loop #{i}', fontsize=14)
    ax[0,i].set_xscale('log')
    ax[0,i].set_ylabel('Gain (dB)', fontsize=14)
    ax[0,i].set_ylim([-120,120])
    ax[0,i].grid(which='major', linewidth="0.5")
    ax[0,i].grid(which="minor", linewidth="0.35")
    ax[0,i].minorticks_on()

    df[df.Step == i].plot(ax=ax[1,i], x="Freq",  y="abs(Zoo)", label=r"|$Z_{O,Open}$|,VRM=OFF")
    df[df.Step == i].plot(ax=ax[1,i], x="Freq",  y="abs(Zoc)", label=r"|$Z_{O,Close}$|,VRM=ON")

    ax[1,i].set_xscale('log')
    ax[1,i].set_ylabel('Gain (dB)', fontsize=14)
    ax[1,i].set_ylim([-120,120])
    ax[1,i].grid(which='major', linewidth="0.5")
    ax[1,i].grid(which="minor", linewidth="0.35")
    ax[1,i].minorticks_on()

plt.savefig("PltTs2.png", format='png', bbox_inches='tight')

plt.show()
plt.close('all')

