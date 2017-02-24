import numpy as np

from numpy import array, asarray, float64, int32, zeros

from scipy.optimize import fmin

from PyFilescripttotal import Iteration


#Gmc = 2 # Toughness fracture (initial value)
#F2t = 30 # Transverse strength in-situ (initial value)

#lb = [1.5, 20] # Initial bound constraint for Gmc and F2t respectively
#ub = [30.5, 141] # Final bound constraint for Gmc and F2t respectively
"""
def func(inp, a, b):
	X = inp[0]
	Y = inp[1]
	fun = a*X**2-b*X+2 
	return fun
"""

# My input variables to optimize
# For fiber: [AlphaLongitudinal, AlphaTransversal]
x0 = array([-1.46e-06, 12.5e-06])
#mybounds = [(0,1), (0,2)]

E = 37876
Area = 13.3
l_o = 135

xopt,fopt,iter,funcalls, warnflag,allvecs = fmin(Iteration, x0, args = (E, Area, l_o), xtol=1e-6,ftol=1e-6, maxiter=None, maxfun=None, full_output=True, retall=True)

print(xopt)
print(fopt)
print(funcalls)
print(allvecs)