#!/usr/bin/python3

import sys
import re

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# runtime: linear O(n) where n is number of tokens in a text file
# description:	each line of a file is grabbed then iterated over,
#				if token is found it is added to list
def getTokens(string: str) -> list:
	tokens = []
	cleanLine = re.split("\W+", string)

	for word in cleanLine:
		if word.isalnum() == True:
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
    updated_tokens = updateStopWords(tokens)
	freqs = computeWordFrequencies(tokenDict, updated_tokens)


def updateStopWords(tokenDict: dict):
    stop_words = set(stopwords.words('english'))
    print(stop_words)
    for i in stop_words:
        del tokenDict[i]
    return tokenDict
    
if __name__ == "__main__":
    sample_dict = {"mahsa":4, "Hello":3}
    updateStopWords(sample_dict)

