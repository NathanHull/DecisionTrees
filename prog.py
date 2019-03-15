import sys
from collections import OrderedDict, defaultdict
from math import log2


class Entry:
	def __init__(self, target):
		self.target = target
		self.values = {}


class Node:
	def __init__(self, name = ''):
		self.name = name
		self.nextNodes = defaultdict()
		self.isLeaf = False


def createNode(currAttr, subset):
	if currAttr in processedAttributes:
		return None
		
	root = Node(currAttr)
	processedAttributes.add(currAttr)

	### USE defaultdict() TO PREVENT KEY ERROR WHEN ADDING 
	### NEW NESTED DICTIONARY KEYS
	# Number of times each attribute has implied each target
	attributeCausations = {}
	for attribute in attributes:
		attributeCausations[attribute] = defaultdict()
		for attributeValue in attributes[attribute]:
			attributeCausations[attribute][attributeValue] = defaultdict()
			for target in targets:
				attributeCausations[attribute][attributeValue][target] = 0

	# Number of times each attribute has occurred
	attributeOccurrences = {}
	for attribute in attributes:
		attributeOccurrences[attribute] = defaultdict()
		for attributeValue in attributes[attribute]:
			attributeOccurrences[attribute][attributeValue] = 0

	# Get number of attribute occurrences and number of times each
	# implies a target
	for entry in entries:
		j = 0
		for attribute in attributes:
			attributeCausations[attribute][line[j]][entry.target] += 1
			attributeOccurrences[attribute][line[j]] += 1
			j += 1

	# Calculate entropies
	# E = -p log2 (p)
	entropies = {}
	setEntropy = 0
	for attribute in attributes:
		entropies[attribute] = defaultdict()
		for attributeValue in attributes[attribute]:
			entropies[attribute][attributeValue] = 0

	for attribute in attributes:
		for attributeValue in attributes[attribute]:
			for target in targets:
				if attributeCausations[attribute][attributeValue][target] != 0 and attributeOccurrences[attribute][attributeValue] != 0:
					entropies[attribute][attributeValue] += attributeCausations[attribute][attributeValue][target] / attributeOccurrences[attribute][attributeValue] * log2(attributeCausations[attribute][attributeValue][target] / attributeOccurrences[attribute][attributeValue])
			entropies[attribute][attributeValue] *= -1
			setEntropy += entropies[attribute][attributeValue]

	print('Calculated set entropy:',setEntropy)

	# Calculate Information Gains
	gains = {}
	for attribute in attributes:
		gains[attribute] = setEntropy

	for attribute in attributes:
		for attributeValue in attributes[attribute]:
			gains[attribute] -= (attributeOccurrences[attribute][attributeValue] / numEntries) * entropies[attribute][attributeValue]
		print(attribute,'gain:',gains[attribute])
	print()

	sortedGains = sorted(gains, key=gains.get, reverse=True)
	targetGain = sortedGains[0]







	# If all attributes have been processed,
	# each must be a leaf giving a target value
	if len(processedAttributes) >= numAttributes:
		for attributeValue in attributes[currAttr]:
			node = Node()
			node.isLeaf = True
			currBest = -1
			for target in targets:
				if attributeCausations[currAttr][attributeValue][target] > currBest:
					node.name = target
					currBest = attributeCausations[currAttr][attributeValue][target]
			root.nextNodes[attributeValue] = node
	# Otherwise, calculate best next gain for each value
	else:
		leafFound = False
		for attributeValue in attributes[currAttr]:
			for target in targets:
				# If we can find a class that basically
				# entirely is defined (90%)
				if attributeOccurrences[currAttr][attributeValue] != 0 and attributeCausations[currAttr][attributeValue][target] / attributeOccurrences[currAttr][attributeValue] >= .9:
					node = Node()
					node.name = target
					node.isLeaf = True
					root.nextNodes[attributeValue] = node
					leafFound = True
					break
			# Otherwise, use new gains
			if not leafFound:
				newSubset = set()
				for entry in subset:
					if entry.values[currAttr] == attributeValue:
						newSubset.add(entry)
				node = createNode(targetGain, newSubset)
				if node is not None:
					root.nextNodes[attributeValue] = node

	return root


def printTree(node):
	if node.isLeaf:
		print(node.name)
		return

	print(node.name,'[ ', end='')
	for nextNode in node.nextNodes:
		print(nextNode,':',node.nextNodes[nextNode].name,end=', ')
	print(']')
	for nextNode in node.nextNodes:
		print(node.name,'--',nextNode,'-->', end=' ')
		printTree(node.nextNodes[nextNode])

if len(sys.argv) < 2 or len(sys.argv) > 3:
	print('Usage error: prog.py (training data file) [test data file]')
	sys.exit()

print('Opening data file', sys.argv[1])
with open(sys.argv[1]) as f:
	print('Reading data')
	lines = f.readlines()

entries = set()
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

### USE defaultdict() TO PREVENT KEY ERROR WHEN ADDING 
### NEW NESTED DICTIONARY KEYS
# Number of times each attribute has implied each target
attributeCausations = {}
for attribute in attributes:
	attributeCausations[attribute] = defaultdict()
	for attributeValue in attributes[attribute]:
		attributeCausations[attribute][attributeValue] = defaultdict()
		for target in targets:
			attributeCausations[attribute][attributeValue][target] = 0

# Number of times each attribute has occurred
attributeOccurrences = {}
for attribute in attributes:
	attributeOccurrences[attribute] = defaultdict()
	for attributeValue in attributes[attribute]:
		attributeOccurrences[attribute][attributeValue] = 0

# Get number of attribute occurrences and number of times each
# implies a target
for i in range(numAttributes + 4, numEntries + numAttributes + 4):
	line = lines[i].strip().split(',')
	j = 0
	target = line[numAttributes]
	entry = Entry(target)
	for attribute in attributes:
		attributeCausations[attribute][line[j]][target] += 1
		attributeOccurrences[attribute][line[j]] += 1
		entry.values[attribute] = line[j]
		j += 1
	entries.add(entry)

# Calculate entropies
# E = -p log2 (p)
entropies = {}
setEntropy = 0
for attribute in attributes:
	entropies[attribute] = defaultdict()
	for attributeValue in attributes[attribute]:
		entropies[attribute][attributeValue] = 0

for attribute in attributes:
	for attributeValue in attributes[attribute]:
		for target in targets:
			if attributeCausations[attribute][attributeValue][target] != 0 and attributeOccurrences[attribute][attributeValue] != 0:
				entropies[attribute][attributeValue] += attributeCausations[attribute][attributeValue][target] / attributeOccurrences[attribute][attributeValue] * log2(attributeCausations[attribute][attributeValue][target] / attributeOccurrences[attribute][attributeValue])
		entropies[attribute][attributeValue] *= -1
		setEntropy += entropies[attribute][attributeValue]

print('Calculated set entropy:',setEntropy,'\n')

# Calculate Information Gains
gains = {}
for attribute in attributes:
	gains[attribute] = setEntropy

for attribute in attributes:
	for attributeValue in attributes[attribute]:
		gains[attribute] -= (attributeOccurrences[attribute][attributeValue] / numEntries) * entropies[attribute][attributeValue]
	print(attribute,'gain:',gains[attribute])
print()

# Recursively create decision tree
sortedGains = sorted(gains, key=gains.get, reverse=True)
processedValues = {}
processedAttributes = set()
firstAttribute = sortedGains[0]
root = createNode(firstAttribute, entries)
printTree(root)
