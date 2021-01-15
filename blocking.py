import csv
import pandas as pd
import itertools
import textdistance
import re
def matchManu(name, manu):
	for a, b in list(itertools.product(name.split(" "), manu.split(" "))):
		if(textdistance.jaccard([a], [b]) > 0):
			return True
	return False

def writeCSV(blocksAbt, blocksBuy):
	with open("abt_blocks.csv", "w", newline="") as file:
		writer = csv.writer(file)
		writer.writerow(["block_key", "product_id"])
		for row in blocksAbt:
			writer.writerow(row)
	file.close()
	with open("buy_blocks.csv", "w", newline="") as file:
		writer = csv.writer(file)
		writer.writerow(["block_key", "product_id"])
		for row in blocksBuy:
			writer.writerow(row)
	file.close()

def detectSpecial(text):
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
	return specialWords

blocksBuy = []
manus = set()
with open('buy.csv', encoding = 'ISO-8859-1') as file:
	reader = csv.DictReader(file)
	for row in reader:
		name = row["name"]
		name = str(name).lower()

		#	Find special words in with and without extra symbols
		specials = set()
		for special in detectSpecial(name):
			specials.add(special)
		for special in detectSpecial(re.sub("[^a-z0-9 ]", "", name)):
			specials.add(special)
		blocksBuy += [(special, row["idBuy"]) for special in list(specials)]
		
		#	Add manufacturer to set
		manu = row["manufacturer"]
		manu = str(manu).lower()
		manu = re.sub("[^a-z0-9 ]", '', manu)
		for manuSplit in manu.split():
			manus.add(manuSplit)
			blocksBuy.append([manuSplit, row["idBuy"]])
file.close()

blocksAbt = []
with open('abt.csv', encoding = 'ISO-8859-1') as file:
	reader = csv.DictReader(file)
	for row in reader:
		name = row["name"]
		name = str(name).lower()
		specials = set()

		#	Find special words in with and without extra symbols
		for special in detectSpecial(name):
			specials.add(special)
		for special in detectSpecial(re.sub("[^a-z0-9 ]", "", name)):
			specials.add(special)
		blocksAbt += [(special, row["idABT"]) for special in list(specials)]
        
        #	Check if a word is in the manufacturer set
		name = re.sub("[^a-z0-9 ]", '', name)
		manu = [(word, row["idABT"]) for word in name.split() if word in manus]
		blocksAbt += manu

file.close()

writeCSV(blocksAbt, blocksBuy)