import textdistance
import pandas as pd
import itertools
import numpy
import csv
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re
from nltk.util import ngrams

def writeCSV(data):
	#	Writes data to the csv file
	with open("task1a.csv", "w", newline="") as file:
		writer = csv.writer(file)
		writer.writerow(["idAbt", "idBuy"])
		for row in data:
			writer.writerow(row)

def matchManu(name, manu):
	#	Checks if a word in the manufacturer
	for a, b in list(itertools.product(name.split(" "), manu.split(" "))):
		if(textdistance.jaccard([a], [b]) > 0):
			return True
	return False

def removeManu(name, manu):
	#	Removes the manufacture name from the product name
	output = name
	for word in manu.split():
		exp = r'\b' + word + r'\b\s+'
		temp = output
		temp = re.sub(exp, "", temp)
		while(temp != output):
			output = temp
			temp = re.sub(exp, "", temp)
		output = temp
	return output

def genCharBigram(word):
	#	Generate bigram for the characters
	output = []
	for i in range(0, len(word)-1):
		output.append(f"{word[i]}{word[i+1]}")
	return output

def genCharTrigram(word):
    output = []
    for i in range(0, len(word)-2):
        output.append(word[i:i+3])
    return output

def detectSpecial(text):
	#	Special words are defined as words that have at least one letter and number, or at least one number and one symbol (e.g. an apostrophe)
	specialWords = []
	for word in text.split():
		letterCount = 0
		numericCount = 0
		specialCount = 0
		for letter in word:
			if(letter.isalpha()):
				letterCount += 1
			elif(letter.isnumeric()):
				numericCount += 1
			else:
				specialCount += 1
		if(letterCount > 0 and numericCount > 0 or numericCount > 0 and specialCount > 0):
			specialWords.append(word)
	if(len(specialWords) > 0):
		return specialWords
	return None

def findCode(text):
	#	Finds a product code on the far right of the name of the product, excluding the last letter of the code
	grouped = text.split()
	if(len(grouped) >= 2 and grouped[-2] == "-"):
		return grouped[-1]
	return None

def scanCode(text, code):
	#	Checks if the product code 
	text = text.replace(" ", "")
	text = text.replace("-", "")
	text = text.replace("/", "")
	if(code in text or code[0:len(code)-1] in text):
		return True
	return False

def removeCode(text, code):
	#	Removes the product code from the name
	return text.replace(" - " + code, "")

#	Store the data
abt_small = pd.read_csv("abt_small.csv", encoding = "ISO-8859-1")
buy_small = pd.read_csv("buy_small.csv", encoding = "ISO-8859-1")

dataA = abt_small[["idABT", "name"]].to_numpy()
dataB = buy_small[["idBuy", "name", "manufacturer"]].to_numpy()

dataA = [[id, str(name).lower()] for id, name in dataA]
dataB = [[id, str(name).lower(), str(manu).lower()] for id, name, manu in dataB]

dataADict = {}
for row in dataA:
	if(row[0] not in dataADict):
		dataADict[row[0]] = {}
		dataADict[row[0]]["name"] = row[1]

dataBDict = {}
for row in dataB:
	if(row[0] not in dataBDict):
		dataBDict[row[0]] = {}
		dataBDict[row[0]]["name"] = row[1]
		dataBDict[row[0]]["manufacturer"] = row[2]

results = []
#	Group all products by their manufacturer
for data in dataB:
	for data2 in dataA:
		if(matchManu(data2[1], data[2])):
			results.append([data2[0], data[0]])

confirmedA = []
confirmedB = []
count = 0
results2 = []
threshold = 61
#	Scanning for code
results = sorted(results, reverse=True)
for a, b in results:
	#	Check if the two words are similar enough to each other
	if(a not in confirmedA and b not in confirmedB and fuzz.token_set_ratio(genCharBigram(dataADict[a]["name"]), genCharBigram(dataBDict[b]["name"])) >= threshold):
		codeA = findCode(dataADict[a]["name"])
		codeB = findCode(dataBDict[b]["name"])
		#	Check if the product code on the far right of the name is in the other name
		if(scanCode(dataBDict[b]["name"], codeA) or (codeB != None and scanCode(dataADict[a]["name"], codeB))):
			confirmedA.append(a)
			confirmedB.append(b)
		else:
			#	Collect the remainders for futher analysis
			results2.append([a,b])

#	Sort the results by the first value in the array
results2.sort()
threshold = 0.3
results3 = []
highestPair = None
highest = -1

#	Collects the highest scoring value for each unique 'a' value
for a, b in results2:
	nameA = dataADict[a]["name"]
	nameB = dataBDict[b]["name"]
	code = findCode(nameA)
	codeB = findCode(nameB)
	nameA = removeCode(nameA, code)
	if(codeB != None):
		nameB = removeCode(nameB, codeB)
	score = fuzz.token_set_ratio(genCharTrigram(nameA), genCharTrigram(nameB))
	#	If it is the first value analysed
	if(highestPair == None):
		highest = score
		highestPair = [a,b]
	#	If the current 'a' value is not the same as the previous
	elif(highestPair[0] != a):
		results3.append(highestPair)
		highest = score
		highestPair = [a,b]
	elif(score > highest):
		highest = score
		highestPair = [a,b]
if(highestPair != None):
	results3.append(highestPair)

#	Find special words, collect them if their special words are a subset of one another
results3 = sorted(results3, reverse=True)
results4 = []
for a, b in results3:	
	if(a in confirmedA or b in confirmedB):
		continue
	nameA = dataADict[a]["name"]
	nameB = dataBDict[b]["name"]
	
	code = findCode(nameA)
	codeB = findCode(nameB)
	nameA = removeCode(nameA, code)
	if(codeB != None):
		nameB = removeCode(nameB, codeB)

	specialWordsA = detectSpecial(nameA)
	specialWordsB = detectSpecial(nameB)
	if(specialWordsA != None and specialWordsB != None):
		specialWordsA = set(specialWordsA)
		specialWordsB = set(specialWordsB)
	else:
		results4.append([a,b])
		continue

	if(specialWordsA.issubset(specialWordsB) or specialWordsB.issubset(specialWordsA)):
		confirmedA.append(a)
		confirmedB.append(b)
	else:
		results4.append([a,b])
		continue


#	Compare their likeness
results5 = []
temp = list(zip(confirmedA, confirmedB))
prints = []
for a, b in results4:
	nameA = dataADict[a]["name"]
	nameB = dataBDict[b]["name"]
	code = findCode(nameA)
	codeB = findCode(nameB)
	nameA = removeCode(nameA, code)
	if(codeB != None):
		nameB = removeCode(nameB, codeB)

	if ([a,b] not in temp):
		results5.append([a, b])
		score = textdistance.cosine(list(ngrams(nameA, 3)), list(ngrams(nameB, 3)))
		prints.append([score, nameA, nameB, a, b])
        
threshold = 0.504

prints.sort(key=lambda x: x[1])
# Skip some duplicate names, increases the average precision and recall
finalData = []
for i in range(0, len(prints)-1):
    if(prints[i][1] == prints[i+1][1]):
        i += 1
        continue
    finalData.append(prints[i])
        

finalData.sort(reverse=True)
for line in finalData:
	if(line[0] > threshold and line[3] not in confirmedA and line[4] not in confirmedB):
		confirmedA.append(line[3])
		confirmedB.append(line[4])

confirmed = list(zip(confirmedA, confirmedB))
confirmed.sort()
writeCSV(confirmed)