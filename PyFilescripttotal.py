import Model
import math




#[Gmc,F2t,E (MPa),Area (mm^2), l_o (mm),Tol (mm)]
def Iteration(x, *args):
	AlphaL = x[0]
	AlphaT = x[1]
	E = args[0]
	Area = args[1]
	l_o = args[2]
	
	model = Model.Model()

	model.Setup(AlphaL, AlphaT)
	
	model.RunJob()
	result = model.GetResult()
	
	alphalongitudinal = result[0]
	alphatransverse = result[1]
	
	#strains = [d / l_o for d in displacements]
	#stresses = [f / Area for f in forces]
	
	#stiffness = [stress / strain / E  for (stress, strain) in zip(stresses, strains)]
	
	#strains = [strain * 100.0 for strain in strains]
	
	#A = dict(zip(strains, stiffness))
	
	#B = {
	#	0.2	        :	0.995,
	#	0.355	    :	0.994,
	#	0.4	        :	0.994,
	#	0.47    	:	0.993,
	#	0.6         :	0.98983,
	#	0.72    	:	0.9855,
	#	0.76	    :	0.955,
	#	0.83	    :	0.931095,
	#	0.88	    :	0.919275,
	#	0.93	    :	0.9088,
	#	0.97	    :	0.901,
	#	1.06	    :	0.884299,
	#	1.11	    :	0.87526,
	#	1.15	    :	0.868063,
	#	1.21	    :	0.857211,
	#	1.26	    :	0.84804,
	#	1.31	    :	0.83872,
	#	1.34		:	0.83303,
	#	1.37		:	0.827259,
	#	1.4	        :	0.8214
	#}
	
	error = 0
	
	#for (experimentalStrain, experimentalStiffness) in B.items():
		#(_, correspondingModelStiffness) = min(A.items(), key=lambda (v, _): abs(v - experimentalStrain))
		##print str(experimentalStiffness) + " " + str(correspondingModelStiffness)
		#error += pow(experimentalStiffness - correspondingModelStiffness, 2)
	
	error = (1.0/2.0) * math.sqrt((alphalongitudinal[153]*1e+06+ 1.0512)**2 + (alphatransverse[153]*1e+06 - 34.524)**2);
	return error


"""
def Scale(start, end, stepCount, step):
	return start + (end - start) * step / (stepCount-1)

var1GmcStart = 5
var1GmcEnd = 30
var1GmcStep = 5
var1StepCount = int((var1GmcEnd - var1GmcStart)/var1GmcStep)+1
var2F2tStart = 20
var2F2tEnd = 120
var2F2tStep = 20
minVar1 = 0
minVar2 = 0
minError = 1e6
var2F2tCount = int((var2F2tEnd - var2F2tStart)/var2F2tStep)+1
for i in range(0, var1StepCount):
	for j in range(0, var2F2tCount):
		var1Gmc = Scale(var1GmcStart, var1GmcEnd, var1StepCount, i) 
		var2F2t = Scale(var2F2tStart, var2F2tEnd, var2F2tCount, j) 
		x = array([var1StepCount, var2F2tCount])
		value = Iteration(x,23540,17.28,55)
		if minError > value:
			minError = value
			minVar1 = var1Gmc
			minVar2 = var2F2t
		print(str(var1Gmc) + " " + str(var2F2t) + " : " + str(value))
		
print(str(minVar1) + " " + str(minVar2) + " : " + str(minError))
"""
