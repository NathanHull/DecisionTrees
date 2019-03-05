import sys
from collections import OrderedDict, defaultdict
from math import log2


if len(sys.argv) < 2 or len(sys.argv) > 3:
	print('Usage error: prog.py (training data file) [test data file]')
	sys.exit()

print('Opening data file', sys.argv[1])
with open(sys.argv[1]) as f:
	print('Reading data')
	lines = f.readlines()

numTargets = int(lines[0])
targets = lines[1].strip().split(',')
numAttributes = int(lines[2])
attributes = OrderedDict()
numEntries = int(lines[numAttributes + 3])

# Parse setup data
for i in range(3, numAttributes + 3):
	line = lines[i].strip().split(',')
	numValues = int(line[1])
	attributeValues = set()
	for j in range(2, numValues + 2):
		attributeValues.add(line[j])
	attributes[line[0]] = attributeValues

print('\nTargets:',targets)
print('\nAttributes:')
for k, v in attributes.items():
	print(k,':',v)
print()

# Number of times each attribute has implied each target
attributeCausations = defaultdict()
for i in attributes:
	attributeCausations[i] = defaultdict()
	for j in attributes[i]:
		attributeCausations[i][j] = defaultdict()
		for k in targets:
			attributeCausations[i][j][k] = 0

# Number of times each attribute has occurred
attributeOccurrences = defaultdict()
for i in attributes:
	attributeOccurrences[i] = defaultdict()
	for j in attributes[i]:
		attributeOccurrences[i][j] = 0

# Cumulative entropy of each attribute
entropies = {}
for i in range(numAttributes + 4, numEntries + numAttributes + 4):
	line = lines[i].strip().split(',')
	j = 0
	for attribute in attributes:
		attributeCausations[attribute][line[j]][line[numAttributes]] += 1
		attributeOccurrences[attribute][line[j]] += 1
		j += 1

