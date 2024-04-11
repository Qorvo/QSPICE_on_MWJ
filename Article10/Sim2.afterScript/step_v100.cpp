// Automatically generated C++ file on Thu Mar 28 07:53:55 2024
//
// To build with Digital Mars C++ Compiler:
//
//    dmc -mn -WD sepia_v106.cpp kernel32.lib

#include <stdio.h>
#include <math.h>
#include <malloc.h>
#include <stdarg.h>
#include <time.h>

union uData
{
	bool b;
	char c;
	unsigned char uc;
	short s;
	unsigned short us;
	int i;
	unsigned int ui;
	float f;
	double d;
	long long int i64;
	unsigned long long int ui64;
	char *str;
	unsigned char *bytes;
};

// int DllMain() must exist and return 1 for a process to load the .DLL
// See https://docs.microsoft.com/en-us/windows/win32/dlls/dllmain for more information.
int __stdcall DllMain(void *module, unsigned int reason, void *reserved) { return 1; }

// #undef pin names lest they collide with names in any header file(s) you might include.
#undef IN
#undef CLK
#undef ctrl

// Use Tr = 1ns or Tf = 1ns, generating ~1GHz frequency contents
#define Tr_Tf 1e-9

typedef struct sPeaks
{
	double			n;
	double			Vpk;
	double			Tpk;
	int				dir;
	struct sPeaks	*next;
} PEAK;

struct sSTEP
{
	int		dir;

	bool	clk;

	double	prevTime;
	double	prevVal;

	double	fltV;
	double	fltT;

	double	Istep;
	double	Tstep;

	int		Nslew;
	double	slew;
	double	slewMax;

	double	preAve;
	double	postAve;
	double	Sum;
	double	N;

	double	period;

	PEAK	*PKhead;
	PEAK	*PKtail;
	PEAK	*PKtmp;

	bool	debug;
};

extern "C" __declspec(dllexport) void step_v100(struct sSTEP **opaque, double t, union uData *data)
{
	double	IN		= data[0].d; // input
	double	CLK		= data[1].d; // input
	double	pTstep	= data[2].d; // input parameter
	double	pTready	= data[3].d; // input parameter
	double	pIstep	= data[4].d; // input parameter
	double	&ctrl	= data[5].d; // output

	if(!*opaque)
	{
		*opaque = (struct sSTEP *) malloc(sizeof(struct sSTEP));
		(*opaque)->dir = (pIstep > 0)? +1:-1;	//Positive Istep (sourcing) makes an overshoot.

		(*opaque)->Tstep = pTstep;
		(*opaque)->Istep = pIstep;

		(*opaque)->Nslew = 0;
		(*opaque)->slew = 0;
		(*opaque)->slewMax = 0;

		(*opaque)->preAve = 0;
		(*opaque)->postAve = 0;
		(*opaque)->Sum = 0;
		(*opaque)->N = 0;

		(*opaque)->period = 999;

		(*opaque)->PKhead = (PEAK *) malloc(sizeof(struct sPeaks));
		(*opaque)->PKhead->n = 1;
		(*opaque)->PKhead->Vpk = 0;
		(*opaque)->PKhead->Tpk = 0;
		(*opaque)->PKhead->dir = (pIstep > 0)? +1:-1;
		(*opaque)->PKhead->next= (PEAK *)NULL;
		(*opaque)->PKtail = (PEAK *)NULL;
		(*opaque)->PKtmp = (*opaque)->PKhead;

		(*opaque)->debug = false;
	}
	struct sSTEP *inst = *opaque;

	ctrl = 0;

	if(t < pTready) {
		// NOP
	} else if(t < pTstep) {
		inst->Sum = inst->Sum + IN;
		inst->N += 1;
		inst->preAve = inst->Sum / inst->N;
	} else if(t < (pTstep + Tr_Tf)) {
		ctrl = (t - pTstep) / Tr_Tf;
	} else if(t < (pTstep + Tr_Tf * 20)) {
		ctrl = 1;
	} else if(t < (pTstep + inst->period * 15)) {

		static int flg = 0;
		ctrl = 1;

		double slew = 0;
		bool c = (CLK > 2.5)? true:false;

		if(flg == 0) {
			inst->PKtmp->Vpk = IN;
			inst->PKtmp->Tpk = t;
			inst->fltV = IN;
			inst->fltT = t;
			inst->clk = c;
			inst->Sum = 0;
			inst->N = 0;
			flg = 1;
		}

		if(c == inst->clk) {
			// NOP
		} else if(c == false) {
			inst->clk = false;
		} else if(c == true) {
			inst->clk = true;

			slew = (IN - inst->fltV) / (t - inst->fltT);
			if(fabs(slew) > fabs(inst->slewMax)) {
				inst->slewMax = slew;
			}

			inst->slew = slew;
			inst->fltT = t;
			inst->fltV = IN;
		}

	// Find Peak
		if((IN * inst->dir) > (inst->PKtmp->Vpk * inst->dir)) {
			inst->PKtmp->Vpk = IN;
			inst->PKtmp->Tpk = t;
		}

		if(((inst->dir < 0) && (slew > 0)) || ((inst->dir > 0) && (slew < 0))) {
			if(inst->Nslew < 5) {
				inst->Nslew++;
			} else if((inst->PKtail != NULL) && ((inst->PKtail->n > 1.75) && (t < (inst->PKtail->Tpk + inst->period * 0.75)))) {
				inst->Nslew = 0;
			} else {
//		printf("STEP: dir=%+2d,t=%10lf,IN=%10lf\n", inst->dir, t, IN);
//		fflush(stdout);
				inst->Nslew = 0;
				inst->PKtail = inst->PKtmp;
				inst->dir = inst->dir * -1;

				inst->PKtmp->next = (PEAK *) malloc(sizeof(struct sPeaks));
				inst->PKtmp->next->n = inst->PKtail->n + 0.5;
				inst->PKtmp->next->Vpk = IN;
				inst->PKtmp->next->Tpk = t;
				inst->PKtmp->next->dir = inst->PKtail->dir * -1;
				inst->PKtmp->next->next = (PEAK *)NULL;
				inst->PKtmp = (PEAK *)inst->PKtmp->next;

				if(inst->PKtail->n <= 1.25) {
					// NOP
				} else if(inst->PKtail->n <= 1.75) {
					inst->period = (inst->PKhead->next->Tpk - inst->PKhead->Tpk) * 2;
				} else {
					inst->period = (inst->PKhead->next->next->Tpk - inst->PKhead->Tpk);
				}
			}
		}

	} else {		// t >= Tstep + inst->period * 15
		ctrl = 1;

		inst->Sum = inst->Sum + IN;
		inst->N += 1;
		inst->postAve = inst->Sum / inst->N;
	}

	inst->prevTime = t;
	inst->prevVal  = IN;
}

extern "C" __declspec(dllexport) double MaxExtStepSize(struct sSTEP *inst)
{
	return 1e-3; // implement a good choice of max timestep size that depends on struct sSTEP
}

extern "C" __declspec(dllexport) void Trunc(struct sSTEP *inst, double t, union uData *data, double *timestep)
{ // limit the timestep to a tolerance if the circuit causes a change in struct sSTEP
	double	IN		= data[0].d; // input
	double	CLK		= data[1].d; // input
	double	pTstep	= data[2].d; // input parameter
	double	pTready	= data[3].d; // input parameter
	double	pIstep	= data[4].d; // input parameter
	double	&ctrl	= data[5].d; // output

	if(t < (pTstep - 50e-6)) {
		// NOP
	} else
	if(t < (pTstep - 10e-6)) {
		*timestep = 1e-6;
	} else
	if(t < (pTstep - 1e-6)) {
		*timestep = 0.1e-6;
	} else
	if(t < (pTstep - 0.1e-6)) {
		*timestep = 0.01e-6;
	} else
	if(t < (pTstep - 0.01e-6)) {
		*timestep = 1e-9;
	} else
	if(t < (pTstep + Tr_Tf * 10)) {
		*timestep = 0.1e-9;
	} else
	if (t < (pTstep + inst->period * 2)) {
		*timestep = 0.05e-9;
	} else
	if (t < (pTstep + inst->period * 15)) {
		*timestep = 2e-9;
	} else {
//		static int flg = 0;
//		if(flg == 0) {
//			printf("STEP: t=%10lf,period=%10lf(us)\n", t, inst->period*1e6);
//			fflush(stdout);
//			flg = 1;
//		}
	}
}

extern "C" __declspec(dllexport) void Destroy(struct sSTEP *inst)
{

	struct sPeaks *now = inst->PKhead;
	while(now != NULL) {
		struct sPeaks *tmp = now;
		now = now->next;
		free(tmp);
	}

	free(inst);

}

