import numpy as np

from numpy import array, asarray, float64, int32, zeros

from scipy.optimize import fmin

import PyFilescripttotal
reload(PyFilescripttotal)
from PyFilescripttotal import Iteration

def CalcPoly(T, A, B, C, D = 0):
	return (A + B * T + C * T * T + D * T * T * T);

# My input variables to optimize
Aa = 38.1095 
Ba = 0.1421
Ca = -1.0461e-4 
		
x0 = array([Aa, Ba, Ca])
#mybounds = [(0,1), (0,2)]

alphalongitudinal = {}
alphatransverse = {}

calculateParametersFromPoly = True #False

if calculateParametersFromPoly:
	Temperatures = [93, 66, 39, 24, 12, -15, -42, -70, -96, -123, -150]
	
	for t in Temperatures:
		alphalongitudinal[t] = CalcPoly(t, -0.5802, 2e-4, 3e-6)
		
	for t in Temperatures:
		alphatransverse[t] = CalcPoly(t, 20.619, 0.0154, -2.1e-4, 8e-7)
else:
	alphalongitudinal[93] = 123
	alphalongitudinal[24] = 123
	
	alphatransverse[93] = 123
	alphatransverse[24] = 123

xopt,fopt,iter,funcalls, warnflag,allvecs = fmin(Iteration, x0, args = (alphalongitudinal, alphatransverse), xtol=1e-3,ftol=1e-3, maxiter=None, maxfun=None, full_output=True, retall=True)

print(xopt)
print(fopt)
print(funcalls)
print(allvecs)