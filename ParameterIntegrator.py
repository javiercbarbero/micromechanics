class ParameterIntegrator:
	def __init__(self, A, B, C, Trmax, Trmin, Tref):
		self.A = A
		self.B = B
		self.C = C
		self.Trmax = Trmax
		self.Trmin = Trmin
		self.Tref = Tref
		self.C0 = self.CalcPoly(Trmax)
		self.C1 = self.CalcPoly(Trmin)
		
	def CalcPoly(self, T):
		return (self.A + self.B * T + self.C * T * T);
		
	def CalcPolyI(self, T):
		return (self.A * T + self.B * T * T / 2 + self.C * T * T * T / 3);

	def Eval(self, T):
		if T > self.Trmax:
			return self.C0
		elif T > self.Trmin:
			return self.CalcPoly(T)
		else:
			return self.C1

	def EvalIntegral(self, T):
		if T > self.Trmax:
			return self.C0 * (T - self.Tref)
		elif T > self.Trmin:
			return self.C0 * (self.Trmax - self.Tref) + self.CalcPolyI(T) - self.CalcPolyI(self.Trmax)
		else:
			return self.C0 * (self.Trmax - self.Tref) + self.CalcPolyI(self.Trmin) - self.CalcPolyI(self.Trmax) + self.C1 * (T - self.Trmin)
