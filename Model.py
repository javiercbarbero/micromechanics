from abaqus import *
from abaqusConstants import *
from section import *
from part import *
from material import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from job import *
from sketch import *
from visualization import *
from optimization import *
from connectorBehavior import *
from abaqusConstants import*
import xlsxwriter
import math
import os
import numpy
import AbaqusScriptFunc2

import ParameterIntegrator
reload(ParameterIntegrator)
from ParameterIntegrator import *

class Model:
	def GetResult(self):
		## NOW, IT RUNS THE .ODB TO GET THE RESULTS
		odb = openOdb(path='Job-1.odb');
		myAssembly = odb.rootAssembly;
		
		for key in session.xyDataObjects.keys():
			del session.xyDataObjects[key]
			
		#Creating a temporary variable to hold the frame repository provides the same functionality and speeds up the process
		frameRepository = odb.steps['Step-1'].frames;
		frameS=[];
		frameIVOL=[];
		alpha1=[];
		alpha2=[];
		alpha3=[];
		temp = [];
		#Establish the number of frames in which  we calculate the average_stress
		
		for n in range(0,len(frameRepository)):
			#Get only the last frame [-1]
			numpy.float64(frameS.insert(0,frameRepository[n].fieldOutputs['E'].getSubset(position=INTEGRATION_POINT)));
			numpy.float64(frameIVOL.insert(0,frameRepository[n].fieldOutputs['IVOL'].getSubset(position=INTEGRATION_POINT)));
			#Total Volume
			Tot_Vol=0;
			#Stress Sum
			Tot_Strain=0;

			for II in range(0,len(frameS[n].values)):
				Tot_Vol=numpy.float64(Tot_Vol)+ numpy.float64(frameIVOL[0].values[II].data);
				Tot_Strain=Tot_Strain+frameS[0].values[II].data * frameIVOL[0].values[II].data;

			#Calculate Average
			Avg_Strain = Tot_Strain/Tot_Vol;
			#print 'Abaqus/Standard Stress Tensor Order:'
			#From Abaqus Analysis User's Manual - 1.2.2 Conventions - Convention used for stress and strain components
			#print 'Average stresses Global CSYS: 11-22-33-12-13-23';
			#print Avg_Strain;
			alpha11 = Avg_Strain[0]#z-component,1-direction
			alpha1.insert(n,alpha11) 
			alpha22 = Avg_Strain[1]#x-component,2-direction
			alpha2.insert(n,alpha22) 
			alpha33 = Avg_Strain[2]#y-component,3-direction in Fig. 6.5
			alpha3.insert(n,alpha33) 
			temp.insert(n, 177 - n)
		
		alpha1t = [0]
		alpha2t = [0]
		alpha3t = [0]
		for i in range(1, len(temp)):
			alpha1t.insert(i, -alpha1[i] + alpha1[i - 1])
			alpha2t.insert(i, -alpha2[i] + alpha2[i - 1])
			alpha3t.insert(i, -alpha3[i] + alpha3[i - 1])
		

		# Create a text.file	
		f = open('result.txt', 'w')
		for i in range(0, len(temp)):
			f.write(str(temp[i]) + " " +str(alpha1t[i]) + " " +str(alpha2t[i]) + " " + str(alpha3t[i]) + "\n")
		f.close()
		
		## Create a excel
		## Create a excel with Strain at each temperature
		#workbook = xlsxwriter.Workbook('Alpha.xlsx')
		#worksheet = workbook.add_worksheet()
		## Initiation values for row and column
		#row = 0
		#col = 0
		## Create the table
		#for n in range(0,len(frameRepository)):
		#	worksheet.write(row, col, alpha1[n])
		#	worksheet.write(row, col+1, alpha2[n])
		#	worksheet.write(row, col+2, alpha3[n])
		#	row += 1
		## we close and save the excel	
		#workbook.close()	
		odb.close()
		
		return alpha1t, alpha2t, alpha3t
		
	def RunJob(self):
		self.job.submit(consistencyChecking=OFF)
		self.job.waitForCompletion()
		
	def Setup(self, 
		Aa = 38.1095, 
		Ba = 0.1421, 
		Ca = -1.0461e-4, 
		Ae = 5032.7732,
		Be = -16.7561,
		Ce = 0.0251,
		Av = 0.3659,
		Bv = -1.1108e-4,
		Cv = -8.608e-7,
		VF = 0.48,
		Trmax = 120,
		Trmin = -100,
		Tref = 177,
		Tend = -200):
		
		#print "Vf %f P0 %f P1 %f P2 %f" % (Vf, P0, P1, P2)
		#print "AlphaL %f AlphaT" % (AlphaL, AlphaT)
		
		#if os.path.exists("Job-1.lck"):
			#os.remove("Job-1.lck")
			
		#Creating new databases. Erases all other data.
		Mdb()
		#It copy and write the AbaqusScriptFunc2 that we need in order to create the constraint equations
		#execfile('AbaqusScriptFunc2.py')
		
		##################################################################################
		#CREATE PART
		##################################################################################
		# VARIABLES
		rf=3.5 #micrometros
		a2 = sqrt((pi*(rf**2))/(2*sqrt(3)*VF));
		a3 = sqrt(3)*a2;
		a1 = a2/4;
		
		
		mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=50.0)
		mdb.models['Model-1'].sketches['__profile__'].rectangle(point1=(0.0, 0.0), 
			point2=(a2, a3))
		mdb.models['Model-1'].Part(dimensionality=THREE_D, name='Part-1', type=
			DEFORMABLE_BODY)
		mdb.models['Model-1'].parts['Part-1'].BaseSolidExtrude(depth=a1, sketch=
			mdb.models['Model-1'].sketches['__profile__'])
		del mdb.models['Model-1'].sketches['__profile__']
		mdb.models['Model-1'].ConstrainedSketch(gridSpacing=0.53, name='__profile__', 
			sheetSize=21.24, transform=
			mdb.models['Model-1'].parts['Part-1'].MakeSketchTransform(
			sketchPlane=mdb.models['Model-1'].parts['Part-1'].faces[4], 
			sketchPlaneSide=SIDE1, 
			sketchUpEdge=mdb.models['Model-1'].parts['Part-1'].edges[7], 
			sketchOrientation=RIGHT, origin=(0.0, 0.0, a1)))
		mdb.models['Model-1'].parts['Part-1'].projectReferencesOntoSketch(filter=
			COPLANAR_EDGES, sketch=mdb.models['Model-1'].sketches['__profile__'])
		mdb.models['Model-1'].sketches['__profile__'].CircleByCenterPerimeter(center=(
			0.0, 0.0), point1=(0.0, rf))
		mdb.models['Model-1'].sketches['__profile__'].CircleByCenterPerimeter(center=(
			a2, a3), point1=(a2+rf, a3))
		mdb.models['Model-1'].parts['Part-1'].PartitionCellBySketch(cells=
			mdb.models['Model-1'].parts['Part-1'].cells.getSequenceFromMask(('[#1 ]', 
			), ), sketch=mdb.models['Model-1'].sketches['__profile__'], sketchPlane=
			mdb.models['Model-1'].parts['Part-1'].faces[4], sketchUpEdge=
			mdb.models['Model-1'].parts['Part-1'].edges[7])
		del mdb.models['Model-1'].sketches['__profile__']
		mdb.models['Model-1'].parts['Part-1'].PartitionCellByExtrudeEdge(cells=
			mdb.models['Model-1'].parts['Part-1'].cells.getSequenceFromMask(('[#1 ]', 
			), ), edges=(mdb.models['Model-1'].parts['Part-1'].edges[3], 
			mdb.models['Model-1'].parts['Part-1'].edges[4], 
			mdb.models['Model-1'].parts['Part-1'].edges[5]), line=
			mdb.models['Model-1'].parts['Part-1'].edges[14], sense=REVERSE)
		mdb.models['Model-1'].parts['Part-1'].PartitionCellByExtrudeEdge(cells=
			mdb.models['Model-1'].parts['Part-1'].cells.getSequenceFromMask(('[#2 ]', 
			), ), edges=(mdb.models['Model-1'].parts['Part-1'].edges[11], 
			mdb.models['Model-1'].parts['Part-1'].edges[12], 
			mdb.models['Model-1'].parts['Part-1'].edges[13]), line=
			mdb.models['Model-1'].parts['Part-1'].edges[16], sense=REVERSE)
		
	
		##################################################################################
		#CREATE MATERIAL
		##################################################################################

		# CREATE MATRIX TEMPERATURE DEPENDENT PROPERTIES FOR 'MATERIAL-1'

		alphaS = ParameterIntegrator(Aa * 1e-6, Ba * 1e-6, Ca * 1e-6, Trmax, Trmin, Tref)
		calcE = ParameterIntegrator(Ae, Be, Ce, Trmax, Trmin, Tref)
		calcV = ParameterIntegrator(Av, Bv, Cv, Trmax, Trmin, Tref)

		Elastic = ()
		for i in range(Trmax, Trmin - 1, -1):
			T = i
			E = calcE.Eval(T)
			v = calcV.Eval(T)
			Elastic += ((E, v, T), )
			
		Expansion = ()
		for i in range(Tref, Tend - 1, -1):
			T = i
			epsT = alphaS.EvalIntegral(T)
			secant = 0
			if T != Tref:
				secant =  epsT / (T - Tref)
			Expansion += ((secant, T), )
			
		mdb.models['Model-1'].Material(name='Material-1')
		mdb.models['Model-1'].materials['Material-1'].Elastic(table=Elastic, temperatureDependency=ON)
		mdb.models['Model-1'].materials['Material-1'].Expansion(table=Expansion, temperatureDependency=ON, 
			zero=Tref)
	
		# FIBER PROPERTIES	
		mdb.models['Model-1'].Material(name='Material-2')
		mdb.models['Model-1'].materials['Material-2'].Elastic(table=((520000, 11952, 
			11952, 0.2107, 0.2107, 0.3506, 6894.8, 6894.8, 3375), ), type=
			ENGINEERING_CONSTANTS)
		mdb.models['Model-1'].materials['Material-2'].Expansion(table=((AlphaL, 
			AlphaT, AlphaT), ), type=ORTHOTROPIC)	
	
		# ASSIGN SECTION
		
		mdb.models['Model-1'].HomogeneousSolidSection(material='Material-1', name=
			'Section-1', thickness=None)
		mdb.models['Model-1'].HomogeneousSolidSection(material='Material-2', name=
			'Section-2', thickness=None)
		mdb.models['Model-1'].parts['Part-1'].Set(cells=
			mdb.models['Model-1'].parts['Part-1'].cells.getSequenceFromMask(('[#1 ]', 
			), ), name='Set-1')
		mdb.models['Model-1'].parts['Part-1'].SectionAssignment(offset=0.0, 
			offsetField='', offsetType=MIDDLE_SURFACE, region=
			mdb.models['Model-1'].parts['Part-1'].sets['Set-1'], sectionName=
			'Section-1', thicknessAssignment=FROM_SECTION)
		mdb.models['Model-1'].parts['Part-1'].Set(cells=
			mdb.models['Model-1'].parts['Part-1'].cells.getSequenceFromMask(('[#6 ]', 
			), ), name='Set-2')
		mdb.models['Model-1'].parts['Part-1'].SectionAssignment(offset=0.0, 
			offsetField='', offsetType=MIDDLE_SURFACE, region=
			mdb.models['Model-1'].parts['Part-1'].sets['Set-2'], sectionName=
			'Section-2', thicknessAssignment=FROM_SECTION)

		# CREATE A CSYS
		mdb.models['Model-1'].parts['Part-1'].DatumCsysByThreePoints(coordSysType=
			CARTESIAN, name='Datum csys-1', origin=(0.0, 0.0, a1), point1=(0.0, 0.0, 
			a1+1), point2=(1.0, 0.0, 0.0))	
	
		# MATERIAL ORIENTATION
		mdb.models['Model-1'].parts['Part-1'].MaterialOrientation(
			additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0
			, axis=AXIS_3, fieldName='', localCsys=
			mdb.models['Model-1'].parts['Part-1'].datums[7], orientationType=SYSTEM, 
			region=Region(
			cells=mdb.models['Model-1'].parts['Part-1'].cells.getSequenceFromMask(
			mask=('[#7 ]', ), )), stackDirection=STACK_3)	
	
		##################################################################################
		#CREATE ASSEMBLY
		##################################################################################	
	
		mdb.models['Model-1'].rootAssembly.DatumCsysByDefault(CARTESIAN)
		mdb.models['Model-1'].rootAssembly.Instance(dependent=ON, name='Part-1-1', 
			part=mdb.models['Model-1'].parts['Part-1'])


		##################################################################################
		#CREATE STEP AND FIELD OUTPUT
		##################################################################################			
	
		mdb.models['Model-1'].StaticStep(initialInc=1.0, maxInc=1.0, maxNumInc=1000, 
			minInc=1.0, name='Step-1', previous='Initial', timePeriod=377.0)
	
		mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(variables=(
			'S', 'PE', 'PEEQ', 'PEMAG', 'LE', 'U', 'RF', 'CF', 'CSTRESS', 'CDISP', 
			'IVOL','THE'))
	
		##################################################################################
		#CREATE MESH
		##################################################################################	

		mdb.models['Model-1'].parts['Part-1'].seedPart(deviationFactor=0.1, 
			minSizeFactor=0.1, size=0.3)
		mdb.models['Model-1'].parts['Part-1'].setElementType(elemTypes=(ElemType(
			elemCode=C3D8R, elemLibrary=STANDARD, secondOrderAccuracy=OFF, 
			kinematicSplit=AVERAGE_STRAIN, hourglassControl=DEFAULT, 
			distortionControl=DEFAULT), ElemType(elemCode=C3D6, elemLibrary=STANDARD), 
			ElemType(elemCode=C3D4, elemLibrary=STANDARD)), regions=(
			mdb.models['Model-1'].parts['Part-1'].cells.getSequenceFromMask(('[#1 ]', 
			), ), ))
		mdb.models['Model-1'].parts['Part-1'].generateMesh()
		mdb.models['Model-1'].rootAssembly.regenerate()

		##################################################################################
		#CREATE PERIODIC BOUNDARY CONDITIONS
		##################################################################################	

		mdb.models['Model-1'].rootAssembly.Set(nodes=(
			mdb.models['Model-1'].rootAssembly.instances['Part-1-1'].nodes,), name='PerBound')
	
		(CoorFixNode,NameRef1, NameRef2,NameRef3)=AbaqusScriptFunc2.PeriodicBound3D(mdb,'Model-1','PerBound',[round(a2,10),round(a3,10),round(a1,10)],)	
	
		##################################################################################
		# SYMMETRIC BOUNDARY CONDITIONS
		##################################################################################

		mdb.models['Model-1'].rootAssembly.Set(faces=
			mdb.models['Model-1'].rootAssembly.instances['Part-1-1'].faces.getSequenceFromMask(
			('[#420 ]', ), ), name='Set-2340')
		mdb.models['Model-1'].XsymmBC(createStepName='Initial', localCsys=None, name=
			'XSYM', region=mdb.models['Model-1'].rootAssembly.sets['Set-2340'])
		mdb.models['Model-1'].rootAssembly.Set(faces=
			mdb.models['Model-1'].rootAssembly.instances['Part-1-1'].faces.getSequenceFromMask(
			('[#2080 ]', ), ), name='Set-2341')
		mdb.models['Model-1'].YsymmBC(createStepName='Initial', localCsys=None, name=
			'YSYM', region=mdb.models['Model-1'].rootAssembly.sets['Set-2341'])
		mdb.models['Model-1'].rootAssembly.Set(faces=
			mdb.models['Model-1'].rootAssembly.instances['Part-1-1'].faces.getSequenceFromMask(
			('[#8044 ]', ), ), name='Set-2342')
		mdb.models['Model-1'].ZsymmBC(createStepName='Initial', localCsys=None, name=
			'ZSYM', region=mdb.models['Model-1'].rootAssembly.sets['Set-2342'])
	
		##################################################################################
		# LOAD TEMPERATURE 
		##################################################################################

		mdb.models['Model-1'].rootAssembly.Set(cells=
			mdb.models['Model-1'].rootAssembly.instances['Part-1-1'].cells.getSequenceFromMask(
			('[#7 ]', ), ), edges=
			mdb.models['Model-1'].rootAssembly.instances['Part-1-1'].edges.getSequenceFromMask(
			('[#fffffff ]', ), ), faces=
			mdb.models['Model-1'].rootAssembly.instances['Part-1-1'].faces.getSequenceFromMask(
			('[#ffff ]', ), ), name='Set-2343', vertices=
			mdb.models['Model-1'].rootAssembly.instances['Part-1-1'].vertices.getSequenceFromMask(
			('[#ffff ]', ), ))
		mdb.models['Model-1'].Temperature(createStepName='Initial', 
			crossSectionDistribution=CONSTANT_THROUGH_THICKNESS, distributionType=
			UNIFORM, magnitudes=(177.0, ), name='Predefined Field-1', region=
			mdb.models['Model-1'].rootAssembly.sets['Set-2343'])
		mdb.models['Model-1'].rootAssembly.Set(cells=
			mdb.models['Model-1'].rootAssembly.instances['Part-1-1'].cells.getSequenceFromMask(
			('[#7 ]', ), ), edges=
			mdb.models['Model-1'].rootAssembly.instances['Part-1-1'].edges.getSequenceFromMask(
			('[#fffffff ]', ), ), faces=
			mdb.models['Model-1'].rootAssembly.instances['Part-1-1'].faces.getSequenceFromMask(
			('[#ffff ]', ), ), name='Set-2344', vertices=
			mdb.models['Model-1'].rootAssembly.instances['Part-1-1'].vertices.getSequenceFromMask(
			('[#ffff ]', ), ))
		mdb.models['Model-1'].Temperature(createStepName='Step-1', 
			crossSectionDistribution=CONSTANT_THROUGH_THICKNESS, distributionType=
			UNIFORM, magnitudes=(-200.0, ), name='Predefined Field-2', region=
			mdb.models['Model-1'].rootAssembly.sets['Set-2344'])
	
	
		##################################################################################
		# JOB
		##################################################################################	

		self.job = mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, 
			explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF, 
			memory=90, memoryUnits=PERCENTAGE, model='Model-1', modelPrint=OFF, 
			multiprocessingMode=DEFAULT, name='Job-1', nodalOutputPrecision=SINGLE, 
			numCpus=1, numGPUs=0, queue=None, resultsFormat=ODB, scratch='', type=
			ANALYSIS, userSubroutine='', waitHours=0, waitMinutes=0)
	
	
	



model = Model()
model.Setup(-1.7954e-06, 7.3321e-06)
model.RunJob()
result = model.GetResult()
"""
for e in result:
	print str(e[0]) + " " + str(e[1])
"""

