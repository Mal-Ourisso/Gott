
import abc
import matplotlib.pyplot as plt

operators = '+-*/^'

operFunctions = {
	'+' : lambda x, y: x+y,
	'-' : lambda x, y: x-y,
	'*' : lambda x, y: x*y,
	'/' : lambda x, y: x/y,
	'^' : lambda x, y: x**y
}

def prio(oper1, oper2):
	if oper1 == oper2:
		return 0
	elif (oper1 in '+-' and oper2 in '*/^') or (oper1 in '*/' and oper2 == '^'):
		return -1
	else:
		return 1

def separate(function_str):
	result = []
	aux = ''
	prev = ''
	for c in function_str:
		if c.isnumeric():
			if prev == '' or prev == '(' or prev in operators or prev.isnumeric:
				aux += c
			else:
				result = False
				break
		elif c in operators:
			if prev == '' or prev == '(':
				aux += c
			elif prev.isnumeric() or prev == ')' or prev == 'x':
				if aux != '':
					result.append(aux)
					aux = ''
				result.append(c)
			else:
				result = False
				break
		elif c == 'x':
			if prev == '' or prev == '(' or prev in operators:
				result.append(aux+c)
				aux = ''
			else:
				result = False
				break
		elif c == '(':
			if prev == '' or prev in operators or prev == '(':
				result.append(c)
			else:
				result = False
				break
		elif c == ')':
			if prev.isnumeric() or prev == 'x' or prev == ')':
				if prev.isnumeric():
					result.append(aux)
					aux = ''
				result.append(c)
		elif c != ' ':
			result = False
			break

		if c != ' ':
			prev = c

	if aux and isinstance(result, list):
		result.append(aux)

	return result

def infixToPosFix(function_str):
	function_sep = separate(function_str)
	if not function_sep:
		return False

	pilha = []
	result = []
	for f in function_sep:
		if f == '(':
			pilha.append(f)
		elif f == ')':
			while pilha[-1] != '(':
				result.append(pilha.pop(-1))
			pilha.pop(-1)
		elif f in '+-':
			while len(pilha) > 0 and pilha[-1] != '(':
				result.append(pilha.pop(-1))
			pilha.append(f)
		elif f in '*/':
			while len(pilha) > 0 and pilha[-1] != '(' and pilha[-1] not in '+-':
				result.append(pilha.pop(-1))
			pilha.append(f)
		elif f == '^':
			while len(pilha) > 0 and pilha[-1] != '(' and pilha[-1] not in '+-' and pilha[-1] not in '*/':
				result.append(pilha.pop(-1))
			pilha.append(f)
		elif f.lstrip('-+').isnumeric() or 'x' in f:
			result.append(f)

	while len(pilha) > 0 and pilha[-1] != '(':
		result.append(pilha.pop(-1))

	return result 

class Function(abc.ABC):

	@abc.abstractmethod
	def __repr__(self):
		pass

	def __add__(self, other):
		return Operator('+', self, other)

	def __sub__(self, other):
		return Operator('-',  self, other)

	def __mul__(self, other):
		return Operator('*',  self, other)

	def __truediv__(self, other):
		return Operator('/',  self, other)

	def __pow__(self, other):
		return Operator('^',  self, other)

	@abc.abstractmethod
	def derivada(self):
		pass

	@abc.abstractmethod
	def __call__(self):
		pass

	def plot(self, x_min=-10, x_max=10, y_min=-10, y_max=10):
			x_size = x_max - x_min
			y_size = y_max - y_min
			x = [x_min + (i+1)/1000*x_size for i in range(1000)]
			y = [self(i) for i in x]
			plt.xlabel('x')
			plt.ylabel('y')
			plt.plot(x, y)
			plt.axis([x_min, x_max, y_min, y_max])
			plt.xticks([i for i in range(x_min, x_max+1)])
			plt.yticks([i for i in range(y_min, y_max+1)])
			plt.grid(True)
			plt.show()

	def savePlot(self, file_name='grafico.png', x_min=-10, x_max=10, y_min=-10, y_max=10):
			x_size = x_max - x_min
			y_size = y_max - y_min
			x = [x_min + (i+1)/1000*x_size for i in range(1000)]
			y = [self(i) for i in x]
			plt.xlabel('x')
			plt.ylabel('y')
			plt.plot(x, y)
			plt.axis([x_min, x_max, y_min, y_max])
			plt.xticks([i for i in range(x_min, x_max+1)])
			plt.yticks([i for i in range(y_min, y_max+1)])
			plt.grid(True)
			plt.savefig(file_name)

def newFunction(func):
	obj = False
	pilha = []
	func = infixToPosFix(func)
	if func:
		obj = True
		for f in func:
			if f.lstrip('-+').isnumeric():
				pilha.append(Constant(f))
			elif 'x' in f:
				pilha.append(Variable(f))
			elif f in operators:
				if len(pilha) >= 2:
					right = pilha.pop(-1)
					left = pilha.pop(-1)
					pilha.append(Operator(f, left, right))
				else:
					obj = False
					break

		if len(pilha) == 1 and obj:
			obj = pilha[0]
		else:
			obj = False

		if isinstance(obj, Operator):
			obj.simplify()

	return obj

class Operator(Function):

	def __init__(self, symbol, left, right):
		self._val = symbol
		self._left = left
		self._right = right

	def simplify(self):
		if isinstance(self._left, Operator):
			self._left = self._left.simplify()
		if isinstance(self._right, Operator):
			self._right = self._right.simplify()

		if isinstance(self._left, Constant) and isinstance(self._right, Constant):
			return Constant(operFunctions[self._val](self._left._val, self._right._val))
		
		if self._val == '+':
			if self._left._val == 0:
				return self._right
			elif self._right._val == 0:
				return self._left
			else:
				return self
		elif self._val == '-':
			if self._left._val == 0:
				return Constant(-self._right._val)
			elif self._right._val == 0:
				return self._left
			else:
				return self
		elif self._val == '*':
			if self._left._val == 0 or self._right._val == 0:
				return Constant(0)
			elif self._right._val == 1:
				return self._left
			elif self._left._val == 1:
				return self._right
			else:
				return self
		elif self._val == '/':
			if self._right._val == 1:
				return self._left
			else:
				return self
		elif self._val == '^':
			if self._right._val == 0 or self._left._val == 1:
				return Constant(1)
			elif self._right._val == 1:
				return self._left
			elif self._left._val == 0:
				return Constant(0)
			else:
				return self
		else:
			return self

	def __repr__(self, prev=''):
		result = ''
		if isinstance(self._left, Operator) and prio(self._val, self._left._val) > 0:
			result += '(' + str(self._left) +')'
		else:
			result += str(self._left)

		result += self._val

		if isinstance(self._right, Operator) and prio(self._val, self._right._val) > 0:
			result += '(' + str(self._right) +')'
		else:
			result += str(self._right)
		return result

	def derivada(self):
		dl = self._left.derivada()
		dr = self._right.derivada()
		d = False
		if self._val in '+-':
			d = operFunctions[self._val](dl, dr)
		elif self._val == '*':
			d = self._left*dr + self._right*dl
		elif self._val == '/':
			if isinstance(self._left, Constant):
				d = dr / self._left
			elif isinstance(self._right, Constant):
				d = dl / self._right
			else:
				d = (self._right*dl - self._left*dr)/(dr**Constant(2))
		elif self._val == '^':
			if isinstance(self._left, Variable) and isinstance(self._right, Constant):
				d = self._right * self._left**(Constant(self._right._val-1))
			else:
				pass

		if isinstance(d, Operator):
			d = d.simplify()

		return d

	def integral(self):
		il = self._left.integral()
		ir = self._right.integral()
		i = False

		if self._val in '+-':
			i = operFunctions[self._val](il, ir)
		elif self._val in '*/':
			if isinstance(self._left, Constant):
				i = operFunctions[self._val](self._left, ir)
			elif isinstance(self._right, Constant):
				i = operFunctions[self._val](self._right, il)
			else:
				pass
		elif self._val == '^':
			if isinstance(self._left, Variable) and isinstance(self._right, Constant):
				newPower = Constant(self._right._val + 1)
				i = (self._left ** newPower)/newPower
			else:
				pass

		return i

	def __call__(self, varVal):
		return operFunctions[self._val](self._left(varVal), self._right(varVal))

class Constant(Function):

	def __init__(self, val):
		self._val = float(val)
		self._left = None
		self._right = None

	def __repr__(self):
		if int(self._val) == self._val:
			result = str(int(self._val))
		else:
			result = "{:.2f}".format(self._val)
		if self._val < 0:
			result = '(' + result + ')'

		return result

	def derivada(self):
		return Constant(0)

	def integral(self):
		return self * Variable('x')

	def __call__(self, varVal):
		return self._val

class Variable(Function):

	def __init__(self, val):
		if val[0] == '+':
			val = val[1:]
		self._val = val
		self._left = None
		self._right = None

	def __repr__(self):
		result = self._val
		if self._val[0] == '-':
			result = '(' + result + ')'
		return result

	def derivada(self):
		return Constant(1)

	def integral(self):
		return (self ** Constant(2))/Constant(2)

	def __call__(self, varVal):
		if self._val[0] == '-':
			varVal *= -1
		return varVal
