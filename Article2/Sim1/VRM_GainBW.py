import subprocess
import qspice
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

#######
# Run QSPICE for ASCII output

qname = r"c:/Program Files/QSPICE/QSPICE64.exe"
qopt = "-ASCII"
fname = "VRM_GainBW"

subprocess.run([qname, qopt, fname + ".cir"])

#######
# Plot

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

q = qspice.Qspice(fname + ".qraw")
q.parse()

val0 = q.get_data('V(vout)',0)
val1 = q.get_data('V(vout)',1)
f=q.get_frequency()

plt.xlabel('Frequency (Hz)', fontsize=14)
plt.ylabel('Gain (dB)', fontsize=14)

plt.xlim(1,10e6)
plt.ylim(-20,160)
plt.xscale('log')
plt.xticks([1,1e1,1e2,1e3,1e4,1e5,1e6,1e7],["1","10","100","1k","10k","100k","1M","10M"])
#plt.yticks([0,20,40,60,80])
plt.plot(f, 20*np.log10(np.absolute(val0)),label="Open Loop")
plt.plot(f, 20*np.log10(np.absolute(val1)),label="Closed Loop")
plt.grid(which='major', linewidth="0.5")
plt.grid(which="minor", linewidth="0.35")
plt.legend(ncol=1, loc="upper right",fancybox=True)

plt.savefig(fname + "_plt.png", format='png', bbox_inches='tight')
plt.show()

