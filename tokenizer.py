#!/usr/bin/python3

import sys
import re

tokenMatch = re.compile("[\s.,!?:;'\"-]+")
# runtime: linear O(n) where n is number of tokens in a text file
# description:	each line of a file is grabbed then iterated over,
#				if token is found it is added to list
def getTokens(string: str) -> list:
	tokens = []
	cleanLine = tokenMatch.split(string)

	for word in cleanLine:
		if word.replace("'", "").isalnum() == True:
			tokens.append(word.lower())

	return tokens

# runtime: linear O(n) where n is size of tokens list
# description:	tokens list is iterated over, add tokens as keys to
#				dict counting # of occurences of each token
def computeWordFrequencies(tokenDict: dict, tokens: list) -> dict:
	for t in tokens:
		if t not in tokenDict:
			tokenDict[t] = 0
		tokenDict[t] += 1

	return tokenDict

# runtime: log-linear O(n*log(n)) where n is number of dict keys
# description:	sort freqencies dict in descending order, then print
#				all key -> value pairs
def printFreqs(freqs: dict) -> None:
	sortedFreqs = sorted(freqs.items(), key=lambda x: x[1], reverse=True)

	for f in sortedFreqs:
		print(f[0] + " = " + str(f[1]))

# runtime: log-linear O(n*log(n)) where n is number of real tokens
# description:	entry point. find tokens, build frequency dict, then
#				sort and print frequency list. bound by printFreqs()
def updateTokenCounts(tokenDict: dict, bodyText: str):
	tokens = getTokens(bodyText)
	freqs = computeWordFrequencies(tokenDict, tokens)
