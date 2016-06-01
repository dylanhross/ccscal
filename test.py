import numpy


def getInputParams(filename):
	params = [[],[],[]]
	with open(filename) as input:
		done = False
		for line in input:
			if not done:
				if line.split()[0] == ";rfn":
					params[0].append(line.split()[2])
				elif line.split()[0] == ";mwn":
					params[0].append(line.split()[2])
				elif line.split()[0] == ";edc":
					params[0].append(line.split()[2])
				elif line.split()[0] == ";cff":
					params[1].append(line.split()[2])
				elif line.split()[0] == ";cdf":
					params[1].append(line.split()[2])
				elif line.split()[0] == ";crd":
					params[2].append(line.split()[2])
					done = True
			else:
				break
	params.append(numpy.genfromtxt(filename, dtype=str, comments=";"))
	return params

data = getInputParams("CcsCalInput_TEMPLATE.txt")

print data
