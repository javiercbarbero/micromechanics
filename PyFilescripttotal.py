import Model
reload(Model)
import math

#[Gmc,F2t,E (MPa),Area (mm^2), l_o (mm),Tol (mm)]
def Iteration(x, *args):
	alphalongitudinal = args[0]
	alphatransverse = args[1]
	
	model = Model.Model()

	model.Setup(Aa = x[0], Ba = x[1], Ca = x[2])
	
	model.RunJob()
	result = model.GetResult()
	
	alpha1t = result[0]
	alpha2t = result[1]
	alpha3t = result[2]
	
	cost = 0
	N = 0
	
	for t, alphaL in alphalongitudinal.iteritems():
		alphaL_experimental = alpha1t[t]
		N += 1
		cost += math.pow(alphaL_experimental - alphaL, 2)
	
	for t, alphaT in alphatransverse.iteritems():
		alphaT_experimental1 = alpha2t[t]
		alphaT_experimental2 = alpha3t[t]
		N += 2
		cost += math.pow(alphaT_experimental1 - alphaT, 2)
		cost += math.pow(alphaT_experimental2 - alphaT, 2)
		
	cost = math.pow(cost, 0.5)
	cost /= N
	
	return cost
	