import sys
import subprocess
import os
import os.path
from os.path import expanduser
from datetime import datetime
import re

import pandas as pd


class PyQSPICE:
    @classmethod
    def _ExecPath(cls):
        cls.gpath = {}
        cls.gpath['cwd'] = os.getcwd()
        cls.gpath['home'] = expanduser("~")
        usrp = cls.gpath['home'] + "/QSPICE/"
        sysp = r"c:/Program Files/QSPICE/"
    
        ux = "QUX.exe"
        qs = "QSPICE64.exe"
        
        for exe in ['QUX', 'QSPICE64']:
            if os.path.isfile(sysp + exe + '.exe'): cls.gpath[exe] = sysp + exe + '.exe'
            if os.path.isfile(usrp + exe + '.exe'): cls.gpath[exe] = usrp + exe + '.exe'
            try: cls.gpath[exe]
            except: print(exe + ".exe not found!") * exit()
             
    def __init__(self, fname):
        PyQSPICE._ExecPath()
        self.path = {}
        self.ts = {}
        self.date = {}
        
        self.sim = {"Nline": 4999, "Nstep": 0}
        
        self.path['user'] = fname
        self.path['base'] = fname.removesuffix('.qsch').removesuffix('.qraw').removesuffix('.cir')
        PyQSPICE.tstime(self, ['qsch', 'qraw', 'cir'])
        
    def setNline(self, i):
        self.Nline = i
    
    def qsch2cir(self):
        if self.ts['qsch']:
            with open(self.path['cir'], "w") as ofile:
                subprocess.run([self.gpath['QUX'], "-Netlist", self.path['qsch'], "-stdout"], stdout=ofile)
                PyQSPICE.tstime(self, ['cir'])
                
    def cir2qraw(self):
        if self.ts['cir']:
            subprocess.run([self.gpath['QSPICE64'], self.path['cir']])
            PyQSPICE.tstime(self, ['qraw'])

    def LoadQRAW(self, probe):
        if self.ts['qraw']:
            plots = ",".join(probe)
            with subprocess.Popen([self.gpath['QUX'], "-Export", self.path['qraw'], plots, str(self.sim['Nline']), "SPICE", "-stdout"], stdout=subprocess.PIPE, text=True) as qux:
                while True:
                    line = qux.stdout.readline()
                    if line == '\n': continue        
                    if line.startswith("Values:"): break
                    if line.startswith("No. Points:"):
                        self.sim['Nstep'] = int(int(re.match('^No. Points:\s*(\d+).*', line).group(1)) / self.sim['Nline'])
                    if line.startswith("Plotname:"):
                        self.sim['Type'] = re.match('^Plotname:\s+(\S.*)$', line).group(1)
                        if self.sim['Type'].startswith("Tran"):
                            self.sim['Xlbl'] = "Time"
                        if self.sim['Type'].startswith("AC"):
                            self.sim['Xlbl'] = "Freq"
                    if line.startswith("Abscissa:"):
                        pat = '^Abscissa:\s+(\S+)\s+(\S+)\s*'
                        self.sim['Xmin'] = float(re.match(pat,line).group(1))
                        self.sim['Xmax'] = float(re.match(pat,line).group(2))
                        
            with subprocess.Popen([self.gpath['QUX'], "-Export", self.path['qraw'], plots, str(self.sim['Nline']), "CSV", "-stdout"], stdout=subprocess.PIPE, text=True) as qux:
                
                head = []
                head.append(self.sim['Xlbl'])
                head.extend(probe)
                
                df = pd.read_csv(qux.stdout, sep='\t', header=0, names=head)
                
                if self.sim['Type'].startswith("AC"):
                    for lbl in probe:
                        df[lbl] = df[lbl].map(lambda x: complex(x.replace(',-','-').replace(',','+') + 'j'))

                tmp = []
                for i in range(self.sim['Nstep']):
                    tmp = tmp + ([i] * (self.sim['Nline']+1))
                df["Step"] = tmp
            return df
                        
    def comp2real(self, df, idx):
        for i in idx:
            df[i] = df[i].map(lambda x: (x).real)
        
        
    def tstime(self, arr):
        for suf in arr:
            self.path[suf] = self.path['base'] + "." + suf
            try: self.ts[suf] = os.path.getmtime(self.path[suf])
            except: self.ts[suf] = 0
            if self.ts[suf]:
                self.date[suf] = datetime.fromtimestamp(self.ts[suf])

        
    @classmethod
    def chdir(cls, dir):
        if os.path.isdir(dir):
            os.chdir(dir)
            cls.gpath['cwd'] = dir
        
    def func2(self):
        self.arere = self.arere + "#"
        
    def func3(self):
        PyQSPICE.qname = "momo"
 