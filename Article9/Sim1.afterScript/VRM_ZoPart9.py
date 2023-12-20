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
fig, ax = plt.subplots(2,2,sharex=True,constrained_layout=True,figsize=(12,6))

for i in [0, 1]:
    df[df.Step == i].plot(ax=ax[0,i], x="Freq",  y="abs(Zoo)", label=r"$Z_{OUT}$,VRM=OFF")
    df[df.Step == i].plot(ax=ax[0,i], x="Freq",  y="abs(Zoc)", label=r"$Z_{OUT}$,VRM=ON")

    ax[0,i].set_title(f'Loop #{i}', fontsize=14)
    ax[0,i].set_xscale('log')
    ax[0,i].set_ylabel('Gain (dB)', fontsize=14)
    ax[0,i].set_ylim([-120,120])
    ax[0,i].grid(which='major', linewidth="0.5")
    ax[0,i].grid(which="minor", linewidth="0.35")
    ax[0,i].minorticks_on()

    df[df.Step == i].plot(ax=ax[1,i], x="Freq",  y="arg(Zoo)", label=r"$Z_{OUT}$,VRM=OFF")
    df[df.Step == i].plot(ax=ax[1,i], x="Freq",  y="arg(Zoc)", label=r"$Z_{OUT}$,VRM=ON")

    ax[1,i].set_ylabel('Phase (°)', fontsize=14)
    ax[1,i].set_xlabel('Frequency (Hz)', fontsize=14)
    ax[1,i].set_ylim([-90,90])
    ax[1,i].grid(which='major', linewidth="0.5")
    ax[1,i].grid(which="minor", linewidth="0.35")
    ax[1,i].minorticks_on()

plt.savefig("PltZo.png", format='png', bbox_inches='tight')

plt.show()
plt.close('all')

############################################

# Calculate Margins
#para = pd.DataFrame({'Step': range(2)})
para = pd.DataFrame(columns=['Step', 'fc', 'pm', 'fg0', 'gmdB', 'gm', 'QTgMAX', 'fQTgMAX', 'ZMAX', 'fZMAX'], index = range(2))
para.loc[:,'Step'] = range(2)

for i in [0,1]:
    (para.iloc[i,1], para.iloc[i,2]) = run.x0pos2neg(df[df.Step == i], "gain", "phase")
    (para.iloc[i,3], para.iloc[i,4]) = run.x0pos2neg(df[df.Step == i], "phase", "gain")
    para.iloc[i,5] = 10 ** (para.iloc[i,4]/20)

############################################

dfQ = pd.DataFrame()

for i in [0,1]:
    dfQ = pd.concat([dfQ, run.QTg( \
            df[df.Step == i].loc[:,[run.sim['Xlbl'],"arg(Zoc)"]].reset_index(drop=True), \
            "fQTg", "QTg", 180/pi).assign(Step=i)], ignore_index=True)

#'QTgMAX', 'fQTg', 'ZMAX'], 
for i in [0,1]:
    idx = dfQ[dfQ.Step == i].loc[:,'QTg'].idxmax()
    para.loc[i,'QTgMAX'] = dfQ.loc[idx,'QTg']
    f= dfQ.loc[idx,'fQTg']
    para.loc[i,'fQTgMAX'] = f
    idx = df[df.Step == i].query('@f / 2 < Freq < @f * 2').loc[:,'abs(Zoc)'].idxmax()
    para.loc[i,'ZMAX'] = df[df.Step == i].loc[idx,'abs(Zoc)']
    para.loc[i,'fZMAX'] = df[df.Step == i].loc[idx,'Freq']

############################################

# Prepare a blank plotting area

for full in [0, 1]:
    fig, ax = plt.subplots(1,2,tight_layout=True)
    #if full == 0: fig.suptitle("Nyquist Diagram, Zoom", fontsize=16)
    #if full == 1: fig.suptitle("Nyquist Diagram, Full", fontsize=16)
    for i in [0,1]:
        df[df.Step == i].plot(ax=ax[i], x="reGain",  y="imGain", label="Loop #1")

        ax[i].set_title(f"Loop #{i}", fontsize = 14)
        if full == 0: ax[i].set_xlim(-2,2)
        if full == 0: ax[i].set_ylim(-2,2)
        ax[i].set_xlabel('')
        ax[i].set_ylabel('')
        ax[i].yaxis.tick_right()
        ax[i].xaxis.tick_top()
        if full == 0: ax[i].set_yticks([-2,-1,0,1,2])
        if full == 0: ax[i].set_xticks([-2,-1,0,1,2])
        ax[i].spines['top'].set_position(('data', 0))
        ax[i].spines['top'].set_color('gray')
        ax[i].spines['right'].set_position(('data', 0))
        ax[i].spines['right'].set_color('gray')
        ax[i].minorticks_off()
        ax[i].get_legend().remove()
        ax[i].set_aspect("equal", adjustable="box")

        if full == 0:
            # Dot-marker at phase-margin
            ax[i].plot(-cos(para.loc[i,"pm"]/180*pi),-sin(para.loc[i,"pm"]/180*pi), marker = 'o')
            aar = linspace(0, 2*pi, 100)
            xar = cos(aar)
            yar = sin(aar)
            ax[i].plot(xar,yar)
    
            # Support-line at phase-margin
            ax[i].plot([-2*cos(para.loc[i,"pm"]/180*pi),0],[-2*sin(para.loc[i,"pm"]/180*pi),0])

            # Label for phase-margin
            arc = linspace(0, para.loc[i,"pm"]/180*pi, 20)
            xarc = -1.5 * cos(arc)
            yarc = -1.5 * sin(arc)
            ax[i].plot(xarc, yarc)
            ax[i].text(-2,-0.3,r"$\phi_m$={:.1f}°".format(para.loc[i,"pm"]))
        
            # Dot-marker at gain-margin
            ax[i].plot(-1 * para.loc[i,"gm"],0,marker = 'o',markersize=4,markeredgecolor="black")
            ax[i].plot([-1 * para.loc[i,"gm"], -1 * para.loc[i,"gm"]], [0,0.4])
            ax[i].text(-0.6,0.5,r"G.M.={:.1f}dB".format(para.loc[i,"gmdB"]))
            
            Zmax = df[(df.Step == i) & (df.Freq == para.loc[i,"fZMAX"])].loc[:,["reGain","imGain"]]
            ax[i].plot(Zmax.iloc[0,0], Zmax.iloc[0,1], marker = 'o',markersize=4,markeredgecolor="green")
            ax[i].plot([Zmax.iloc[0,0],-1], [Zmax.iloc[0,1],0],color="green")
            ax[i].text(Zmax.iloc[0,0]+0.1,Zmax.iloc[0,1] - 0.1,"Stability Margin",size=8,color="green")
    
    if full == 0: plt.savefig("PltNyZ.png", format='png', bbox_inches='tight')
    if full == 1: plt.savefig("PltNyF.png", format='png', bbox_inches='tight')
    plt.show()
        
plt.close('all')

############################################

plt.close('all')
fig, ax = plt.subplots(tight_layout=True)

for i in [0, 1]:
    df[df.Step == i].plot(ax=ax, x="Freq", y="abs(Zoc)", label=f"Loop #{i}")

    ax.set_xscale('log')
    ax.set_xlabel('Frequency (Hz)', fontsize=14)
    ax.set_ylabel('$Z_{OUT(Closed)}$ (VRM=ON) (dB)', fontsize=14)
    ax.minorticks_on()
    ax.grid(which='major', linewidth="0.5")
    ax.grid(which='minor', linewidth="0.35")
    
    tmp = para.loc[i, 'ZMAX']
    ax.plot([para.loc[i,"fZMAX"], para.loc[i,"fZMAX"]], [tmp-10,tmp+10], linewidth=1, linestyle="dotted")
    ax.plot([100,1e7], [tmp, tmp], linewidth=1, linestyle='dotted')

plt.legend(ncol=1, loc="upper right",fancybox=True)
plt.savefig("PltZoP.png", format='png', bbox_inches='tight')

plt.show()

############################################

plt.close('all')
plt.style.use('ggplot')
fig, ax = plt.subplots(tight_layout=True)

for i in [0, 1]:
    dfQ[dfQ.Step == i].plot(ax=ax, x="fQTg",  y="QTg", label=f"Loop #{i}")

    ax.set_xscale('log')
    ax.set_xlabel('Frequency (Hz)', fontsize=14)
    ax.set_ylabel('Q(Tg)', fontsize=14)
    ax.minorticks_on()
    ax.grid(which='major', linewidth="0.5")
    ax.grid(which='minor', linewidth="0.35")

    ax.plot([para.loc[i,"fQTgMAX"], para.loc[i,"fQTgMAX"]], [-0.5,3], linewidth=1, linestyle="dotted")
    #ax.plot([0.9 * para.loc[i, 'fQTgMAX'], 1.1 * para.loc[i, 'fQTgMAX']], [para.loc[i,'QTgMAX'], para.loc[i, 'QTgMAX']], linewidth=1, linestyle='dotted')
    ax.plot([100,1e7], [para.loc[i,'QTgMAX'], para.loc[i, 'QTgMAX']], linewidth=1, linestyle='dotted')

plt.legend(ncol=1, loc="upper right",fancybox=True)
plt.savefig("PltQTg.png", format='png', bbox_inches='tight')

plt.show()

############################################

print(f"           Bode    Zo-Reconstruction")

for i in [0, 1]:
    pm_nism = subprocess.check_output( \
        ["nism.exe", f"{para.loc[i,'fZMAX']}", f"{para.loc[i, 'fQTgMAX']}", f"{para.loc[i, 'QTgMAX']}"])
    print(f"Loop #{i}: {para.loc[i, 'pm']:>8.1f}, {float(pm_nism.decode()):>8.1f}")

