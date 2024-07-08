# RF Signal Integrity to Power Integrity:  Part 11 SEPIA on Time-Domain for ZOUT

## Copyright Notice

````
========  SEPIA on QSPICE V202  ========
This "SEPIA" compiled binary (.dll) is Copyright © 2014 Picotest.
All rights reserved.
Please contact info@picotest.com for more information.
========================================
````

This folder contains the 1st simulation of the  
["part11"](https://www.microwavejournal.com/blogs/32-rf-signal-integrity-to-power-integrity/post/42280-loop-analysis-directly-from-time-domain-waveform-with-sepia) of a series blog/article  
[RF Signal Integrity to Power Integrity](https://www.microwavejournal.com/blogs/32-rf-signal-integrity-to-power-integrity) on  
[Microwave Journal](https://www.microwavejournal.com/).


# Install PyQSPICE First!

In your cmd.exe window.
```
> pip install PyQSPICE
```

# SEPIA@QSPICE Module

This article #11 features [SEPIA@QSPICE](https://github.com/Qorvo/SEPIA_at_QSPICE) module.
Please check the [module usage](https://github.com/Qorvo/SEPIA_at_QSPICE/blob/main/usage.ipynb), [module parameters](https://github.com/Qorvo/SEPIA_at_QSPICE/blob/main/params.md) and [usage from PyQSPICE](https://github.com/Qorvo/SEPIA_at_QSPICE/blob/main/pyparams.md).

## Before Python Script

This folder contains files before running the Python Script.
The [**"Sim1.afterScript"**](https://github.com/Qorvo/QSPICE_on_MWJ/tree/main/Article11/Sim1.afterScript) folder next to this-folder is "after running script".


## Overview Part 11, Sim #1

In Part-11, throughout [QSPICE](qspice.com) simulations, we review Time-Domain base ZOUT with SEPIA.

In this Sim-1, we confirm that SEPIA can extract output impedance model, closely matching to the original.
We start from the exact model SEPIA runs model-fitting, model-#0 of 2 models, and we confirm SEPIA can re-generate the same circuit.

This Sim 1 is a confirmation ONLY of the tool, please check the [**"Sim3"**](https://github.com/Qorvo/QSPICE_on_MWJ/tree/main/Article11/Sim3) fol for the benefit of SEPIA.

## 1. Schematic and Netlists

We use below schmatic and generates 2 netlists for transient (time-domain) and AC (frequency-domain).

**NOTE:** A _gray box_ is a QSPICE's **"C++ => .DLL" SEPIA block**.


```python
from PIL import Image
Image.open("Zo_SEPIA0.sch.png")
```




    
![png](Zo_SEPIA0.sch.png)
    



In this model, we know the Quality factor from this simple equation.

$$
Q = \frac{\sqrt{\frac{L1}{C_{OUT}}}}{R_{DCR} + R_{ESR}}
$$

From the component values in the schematic, we have Q = 5.59.


```python
from PyQSPICE import clsQSPICE as pqs

import re
import subprocess
import math
import cmath

import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as pat
from matplotlib.transforms import ScaledTranslation as stran

import numpy as np
from numpy import sin, cos, pi, linspace

fname = "Zo_SEPIA0"
run = pqs(fname)
run.qsch2cir()
run.cir4label('ac')
run.cir4label('tran')
```

## 2. AC Simulation: Reference Data

First, we run an AC simulation for our reference data.

From the Q(Tg) plot, we can confirm that this circuit shows Q = 5.5.


```python
Ndata = 1024 * 2
run.selectSimLabel('ac', Nline = Ndata)

run.cir2qraw()

v = "V(out)"
i = "I(Iac)"

dfAC = run.LoadQRAW([v])

dfAC = run.GainPhase(dfAC, v, "abs(Zoac)", "arg(Zoac)")
run.comp2real(dfAC, ["Step", "abs(Zoac)", "arg(Zoac)", run.sim['Xlbl']])
#print(dfAC)

dfQ = pd.DataFrame()
dfQ = run.QTg(dfAC.loc[:,["Freq","arg(Zoac)"]], "fQTg", "QTg", 180/pi)
#print(dfQ)

plt.close('all')

fig, (axT, axM, axB) = plt.subplots(3, 1, sharex=True, constrained_layout=True)

dfAC.plot(ax=axT, x="Freq", y="abs(Zoac)", label="Output Impedance")
dfAC.plot(ax=axM, x="Freq", y="arg(Zoac)", label="Phase")
dfQ.plot(ax=axB, x="fQTg", y="QTg")
run.PrepFreqImpePlot(axT, "Frequency (Hz)", r"$Z_{OUT}$ ($\Omega$)", "auto", [-80,40], "")
run.PrepFreqGainPlot(axM, "Frequency (Hz)", r"Phase (°)", [100,1e6], [-120,120], "")
run.PrepFreqGainPlot(axB, "Frequency (Hz)", r"Q(Tg)", [100,1e6], [-5,15], "")

plt.savefig("Zo_SEPIA0.ac.png", format='png', bbox_inches='tight')

plt.show()
```


    
![png](Zo_SEPIA0.ac.png)
    


## 3. Transient Simulation: Step-Load

Now, we run a transient simulation with the SEPIA C++ Block driven step current load.

As we have Q = 5.5, we can see heavy ringing.

As a result of this simulation run with the SEPIA C++ block, it outputs the result of model fitting (which is expected to be identical to the original simulation).


```python
Ndata = 1024
run.selectSimLabel('tran', Nline = Ndata, Nbit = 80)

sepiaTran = "_sepia_tran"
sepiaAC   = "_sepia_ac"
sepiaLog  = "_sepia_log"
run.opt4SEPIA(run.path['tran.cir'], prnPeak = True, Verbose = True,
              fnTran0 = sepiaTran, runTran0 = False, fnAC0 = sepiaAC, runAC0 = False, fnLog = sepiaLog)
    
run.cir2qraw()
#run.copy2qraw()  #use this line to re-use existing QRAW file

v = "V(out)"
i = "I(G1)"

dfTRAN = run.LoadQRAW([v,i])
#print(dfTRAN)

plt.close('all')

fig, ax = plt.subplots(2, 2, constrained_layout=True)

for n in [0, 1]:
    dfTRAN.plot(ax=ax[0,n], x="Time", y=v, label="V(OUT)")
    dfTRAN.plot(ax=ax[1,n], x="Time", y=i, label="I(Istep)")

run.PrepTimePlot(ax[0,0], "Time", r"V(OUT)", "auto", [4.9,5.1], "")
run.PrepTimePlot(ax[1,0], "Time", r"I(Istep)", "auto", [-2.5,0.5], "")
run.PrepTimePlot(ax[0,1], "Time", r"V(OUT)",   [0.8e-3,1.2e-3], [4.9,5.1], "")
run.PrepTimePlot(ax[1,1], "Time", r"I(Istep)", [0.8e-3,1.2e-3], [-2.5,0.5], "")

plt.savefig("Zo_SEPIA0.tran.png", format='png', bbox_inches='tight')

plt.show()
```


    
![png](Zo_SEPIA0.tran.png)
    


## 4. Transient Result from SEPIA Model-Fitting

### 4.1  Before running a simulation on the SEPIA output

Because of this Sim 1 setup, regenerating itself, it's obvious that SEPIA did a good job When we review the SEPIA output of its model-fitting.


```python
run2 = pqs(sepiaTran)

with open(run2.path['cir'], encoding='SJIS') as f: print(f.read())
with open(sepiaLog + ".log") as f: print(f.read())
```

    * This file is generated by the SEPIA on QSPICE v202.
    Vbias N03 0   5.00000000e+00
    Rdcr N03 N02   2.00001332e-03
    Lout N02 SEPIA_MODEL_FITTING   4.98001407e-08
    Resr 0 N01   2.01679264e-03
    Cout N01 SEPIA_MODEL_FITTING   9.95980483e-05
    
    Istep 0 SEPIA_MODEL_FITTING pwl 0 0   1.00000000e-03 0   1.00000100e-03  -2.00000000e+00
    .TRAN 0   2.00000000e-03 0 10n
    .PLOT TRAN V(SEPIA_MODEL_FITTING)
    
    
    SEPIA: Tready=  0.000900, Tstep=  0.001000, Istep= -2.000000, Option:pvl_sepia_log:t0_sepia_tran:a0_sepia_ac:x
    SEPIA: fTran0=_sepia_tran (Auto-Sim: OFF)
    SEPIA: fAC0=_sepia_ac (Auto-Sim: OFF)
    SEPIA: log=_sepia_log
    
    
    ========  SEPIA Result Begin  ========
    SEPIA: Q= 5.57, Icoil/2=2.22e-15, f=70.89(kHz), T=14.11(us), PM=10.26(deg),
    SEPIA: Z=2.24e-02, L=4.98e-08, C=9.96e-05, 
    SEPIA: (sL+Rcoil) // ((1/sC)+Rcap) Modeling
      Rcoil+Rcap=4.02e-03,  Rcoil=2.00e-03,   Rcap=2.02e-03, 
    SEPIA: (sL) // (1/sC) // Rdump Modeling
      Rdump=1.24e-01,  Rcoil=2.00e-03, 
    SEPIA: preAve=5.00e+00, postAve=5.00e+00
    ========  SEPIA Result End    ========
    SEPIA: n= 1.0, Vpk= -0.038837, Tpk=  3.326000(us), Tpp=  0.000000(us), dir=-1
    SEPIA: n= 1.5, Vpk= +0.029288, Tpk= 10.379100(us), Tpp= 14.106200(us), dir=+1
    SEPIA: n= 2.0, Vpk= -0.022088, Tpk= 17.432200(us), Tpp= 14.106200(us), dir=-1
    SEPIA: n= 2.5, Vpk= +0.016657, Tpk= 24.485300(us), Tpp= 14.106200(us), dir=+1
    SEPIA: n= 3.0, Vpk= -0.012561, Tpk= 31.538300(us), Tpp= 14.106000(us), dir=-1
    SEPIA: n= 3.5, Vpk= +0.009471, Tpk= 38.591400(us), Tpp= 14.106200(us), dir=+1
    SEPIA: n= 4.0, Vpk= -0.007141, Tpk= 45.644700(us), Tpp= 14.106600(us), dir=-1
    SEPIA: n= 4.5, Vpk= +0.005384, Tpk= 52.698000(us), Tpp= 14.106600(us), dir=+1
    SEPIA: n= 5.0, Vpk= -0.004060, Tpk= 59.751100(us), Tpp= 14.106200(us), dir=-1
    SEPIA: n= 5.5, Vpk= +0.003061, Tpk= 66.804300(us), Tpp= 14.106400(us), dir=+1
    SEPIA: n= 6.0, Vpk= -0.002308, Tpk= 73.857400(us), Tpp= 14.106200(us), dir=-1
    SEPIA: n= 6.5, Vpk= +0.001740, Tpk= 80.910700(us), Tpp= 14.106600(us), dir=+1
    SEPIA: n= 7.0, Vpk= -0.001312, Tpk= 87.963800(us), Tpp= 14.106200(us), dir=-1
    SEPIA: n= 7.5, Vpk= +0.000989, Tpk= 95.016700(us), Tpp= 14.105800(us), dir=+1
    SEPIA: n= 8.0, Vpk= -0.000746, Tpk=102.070100(us), Tpp= 14.106800(us), dir=-1
    SEPIA: n= 8.5, Vpk= +0.000562, Tpk=109.123400(us), Tpp= 14.106600(us), dir=+1
    SEPIA: n= 9.0, Vpk= -0.000424, Tpk=116.176300(us), Tpp= 14.105800(us), dir=-1
    SEPIA: n= 9.5, Vpk= +0.000319, Tpk=123.229400(us), Tpp= 14.106200(us), dir=+1
    SEPIA: n=10.0, Vpk= -0.000241, Tpk=130.282700(us), Tpp= 14.106600(us), dir=-1
    SEPIA: n=10.5, Vpk= +0.000181, Tpk=137.336100(us), Tpp= 14.106800(us), dir=+1
    SEPIA: n=11.0, Vpk= -0.000137, Tpk=144.389200(us), Tpp= 14.106200(us), dir=-1
    SEPIA: n=11.5, Vpk= +0.000103, Tpk=151.442300(us), Tpp= 14.106200(us), dir=+1
    SEPIA: n=12.0, Vpk= -0.000077, Tpk=158.495400(us), Tpp= 14.106200(us), dir=-1
    SEPIA: n=12.5, Vpk= +0.000058, Tpk=165.548700(us), Tpp= 14.106600(us), dir=+1
    SEPIA: n=13.0, Vpk= -0.000044, Tpk=172.602000(us), Tpp= 14.106600(us), dir=-1
    SEPIA: n=13.5, Vpk= +0.000033, Tpk=179.655200(us), Tpp= 14.106400(us), dir=+1
    SEPIA: n=14.0, Vpk= -0.000025, Tpk=186.708300(us), Tpp= 14.106200(us), dir=-1
    SEPIA: n=14.5, Vpk= +0.000019, Tpk=193.761400(us), Tpp= 14.106200(us), dir=+1
    SEPIA: n=15.0, Vpk= -0.000014, Tpk=200.814700(us), Tpp= 14.106600(us), dir=-1
    SEPIA: n=15.5, Vpk= +0.000010, Tpk=207.867800(us), Tpp= 14.106200(us), dir=+1
    SEPIA: n=16.0, Vpk= +0.000000, Tpk=211.592700(us), Tpp=  7.449800(us), dir=-1
    
    
    ========  SEPIA on QSPICE V202  ========
    This "SEPIA" compiled binary (.dll) is Copyright ﾂｩ 2014 Picotest.
    All rights reserved.
    Please contact info@picotest.com for more information.
    ========================================
    
    

### 4.2  Transient Simulation on SEPIA Output, Comparison



```python
Ndata = 1024
run2.setNline(Ndata)
run2.setNbit(80)
run2.cir2qraw()
#run.copy2qraw()  #use this line to re-use existing QRAW file

v2 = "V(SEPIA_MODEL_FITTING)"
i2 = "I(Istep)"

dfTRAN2 = run2.LoadQRAW([v2,i2])
print(dfTRAN2)

plt.close('all')

fig, ax = plt.subplots(2, 2, constrained_layout=True)

for n in [0, 1]:
    dfTRAN2.plot(ax=ax[0,n], x="Time", y=v2, label="SEPIA MODEL FIT")
    dfTRAN2.plot(ax=ax[1,n], x="Time", y=i2, label="SEPIA MODEL FIT")
    dfTRAN.plot(ax=ax[0,n], x="Time", y=v, label="ORIGINAL", linestyle="dotted", linewidth=2)
    dfTRAN.plot(ax=ax[1,n], x="Time", y=i, label="ORIGINAL", linestyle="dotted", linewidth=2)


run2.PrepTimePlot(ax[0,0], "Time", r"V(OUT)", "auto", [4.95,5.05], "")
run2.PrepTimePlot(ax[1,0], "Time", r"I(Istep)", "auto", [-2.5,0.5], "")
run2.PrepTimePlot(ax[0,1], "Time", r"V(OUT)",   [1e-3,1.1e-3], [4.95,5.05], "")
run2.PrepTimePlot(ax[1,1], "Time", r"I(Istep)", [1e-3,1.1e-3], [-2.5,0.5], "")

plt.savefig("SEPIA_OUT0.tran.png", format='png', bbox_inches='tight')

plt.show()
```

              Time  V(SEPIA_MODEL_FITTING)  I(Istep)  Step
    0     0.000000                   5.000         0     0
    1     0.000002                   5.000         0     0
    2     0.000004                   5.000         0     0
    3     0.000006                   5.000         0     0
    4     0.000008                   5.000         0     0
    ...        ...                     ...       ...   ...
    1020  0.001992                   4.996        -2     0
    1021  0.001994                   4.996        -2     0
    1022  0.001996                   4.996        -2     0
    1023  0.001998                   4.996        -2     0
    1024  0.002000                   4.996        -2     0
    
    [1025 rows x 4 columns]
    


    
![png](SEPIA_OUT0.tran.png)
    


### 4.3  AC Simulation on SEPIA Output, Comparison



```python
run3 = pqs(sepiaAC)

Ndata = 1024
run3.setNline(Ndata)
run3.setNbit(80)
run3.cir2qraw()

v3 = "V(SEPIA_MODEL_FITTING)"
i3 = "I(Iac)"

dfAC2 = run3.LoadQRAW([v3,i3])

dfAC2 = run.GainPhase(dfAC2, v3, "abs(Zoac)", "arg(Zoac)")
run.comp2real(dfAC2, ["Step", "abs(Zoac)", "arg(Zoac)", run3.sim['Xlbl']])

plt.close('all')

fig, (axT, axB) = plt.subplots(2, 1, sharex=True, constrained_layout=True)

dfAC2.plot(ax=axT, x="Freq", y="abs(Zoac)", label="SEPIA MODEL FIT")
dfAC2.plot(ax=axB, x="Freq", y="arg(Zoac)", label="SEPIA MODEL FIT")

dfAC.plot(ax=axT, x="Freq", y="abs(Zoac)", label="ORIGINAL", linestyle="dotted", linewidth=2)
dfAC.plot(ax=axB, x="Freq", y="arg(Zoac)", label="ORIGINAL", linestyle="dotted", linewidth=2)

run.PrepFreqImpePlot(axT, "Frequency (Hz)", r"$Z_{OUT}$ ($\Omega$)", "auto", [-80,40], "")
run.PrepFreqGainPlot(axB, "Frequency (Hz)", r"Phase (°)", [100,1e6], [-120,120], "")

plt.savefig("SEPIA_OUT0.ac.png", format='png', bbox_inches='tight')

plt.show()
```


    
![png](SEPIA_OUT0.ac.png)
    


## 5. Notes on Model Fitting #0

The SEPIA routine can extract C and L value pair precisely, then, we need to pay attention how we place dumping resistors $R_{DUMP}$ which determines the Q.  In this model, we have $R_{ESR}$ and $R_{DCR}$ in series of corresponding C and L.

From the load-regulation, the difference between pre-step voltage and post-step voltage, the program find $R_{DCR} = (V_{Post-STEP} - V_{Pre-STEP}) / I_{STEP}$, so in this model, all the rest of dumping resisotr amount goes to $R_{ESR}$.

$$
R_{ERS} = R_{DUMP} - R_{DCR}
$$

In a low Q situation (= high $R_{DUMP}$), we may have high ESR which makes a transient response of extracted model off the target.
In such cases, we use model #1 ([**"Sim2"**](https://github.com/Qorvo/QSPICE_on_MWJ/tree/main/Article11/Sim2)).

## 6. Cleaning

Removing 1GB data file.


```python
run.clean(['tran.qraw'])
run2.clean(['qraw'])
run3.clean(['qraw'])
```
