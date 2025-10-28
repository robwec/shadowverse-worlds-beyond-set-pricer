import numpy as np
from tqdm import tqdm
from collections import Counter

##goal: figure out how much it actually costs to get 3x all cards for Shadowverse Beyond
'''
mechanics: 
1. packs can be bought in bulk for 100 crystals each. Crystals are purchased with real money, the best deal being the 5000 crystals for $80. That gets you 50 packs.
2. 4 different rarities: sets consist of bronze, silver, gold, and legendary cards. Packs have eight cards. The first seven cards have one rarity distribution, while the last card is always silver or above.
	Legendary: 1.5%
	Gold: 6%
	Silver: 25%
	Bronze: 67.5%
		really be 67.44% but let's make it all even because we don't know what the remaining 0.06% is
	
	8th card is Silver: 92.44% and Bronze: 0%
	
Additionally, every ten packs you buy you get a guaranteed legendary. (You have a natural 70% chance of getting a legendary anyway, e.g. 1 - 0.985^80 = 0.70153...). The pack counter resets when you get a legendary.
3. Once you have over 3x copies of a card, additional copies can be smelted for vials. Vials can be spent to craft individual cards at a high cost. When buying for completion, legendaries are the most likely cards to be crafted. We will call a set complete once there is enough smelt value to craft the remaining copies of all cards.
Smelt Value:
	Bronze: 10
	Silver: 20
	Gold: 200
	Legendary: 1200
Vial craft cost:
	Bronze: 50
	Silver: 90
	Gold: 750
	Legendary: 3500

The Task:
Using the set distributions and probabilities, run a simulation that runs until you can have 3x of all cards, and returns the crystal and dollar cost of achieving this. Average like 1000 simulations for an average cost at the end.

Brief solution:
base set (Legends Rise) ~= $640
each expansion set ~= $400

So at set 4 you can expect the price of acquiring everything to cost about $640 + $400*3 = $1840 on average. This is not a cheap game, unless you only play 1-2 deck types and even then some of them need a lot of legendaries which will cost $ to acquire quickly (i.e. before the next expansion drops).
'''

##rarity smelt/craft values
bronze_smelt_value = 10
silver_smelt_value = 20
gold_smelt_value = 200
legendary_smelt_value = 1200

bronze_craft_value = 50
silver_craft_value = 90
gold_craft_value = 750
legendary_craft_value = 3500

##Set rarity counts.
set_heirs_of_the_omen = {
	'bronze': 23,
	'silver': 22,
	'gold': 16,
	'legendary': 16,
}
cardlist_ho = ['ie_bronze_'+str(i+1).zfill(3) for i in range(set_heirs_of_the_omen['bronze'])] + ['ie_silver_'+str(i+1).zfill(3) for i in range(set_heirs_of_the_omen['silver'])] + ['ie_gold_'+str(i+1).zfill(3) for i in range(set_heirs_of_the_omen['gold'])] + ['ie_legendary_'+str(i+1).zfill(3) for i in range(set_heirs_of_the_omen['legendary'])]

set_infinity_evolved = {
	'bronze': 23,
	'silver': 22,
	'gold': 16,
	'legendary': 16,
}
cardlist_ie = ['ie_bronze_'+str(i+1).zfill(3) for i in range(set_infinity_evolved['bronze'])] + ['ie_silver_'+str(i+1).zfill(3) for i in range(set_infinity_evolved['silver'])] + ['ie_gold_'+str(i+1).zfill(3) for i in range(set_infinity_evolved['gold'])] + ['ie_legendary_'+str(i+1).zfill(3) for i in range(set_infinity_evolved['legendary'])]

set_legends_rise = {
	'bronze': 45,
	'silver': 37,
	'gold': 37,
	'legendary': 23,
}
cardlist_lr = ['lr_bronze_'+str(i+1).zfill(3) for i in range(set_legends_rise['bronze'])] + ['lr_silver_'+str(i+1).zfill(3) for i in range(set_legends_rise['silver'])] + ['lr_gold_'+str(i+1).zfill(3) for i in range(set_legends_rise['gold'])] + ['lr_legendary_'+str(i+1).zfill(3) for i in range(set_legends_rise['legendary'])]

##We will do "collections" per set rather than across all sets

mycollection = Counter(); my_vials = 0
def calculateCollectionVialCompletionCost(mycollection, mysetcardlist, use_1x_legendaries_limit=False):
	totalvialcraftcost = 0
	
	n_missing_bronzes = 0
	set_bronzes = [x for x in mysetcardlist if 'bronze' in x]
	for i in range(len(set_bronzes)):
		thisbronze = set_bronzes[i]
		n_missing_bronzes += max(3 - mycollection[thisbronze], 0)
	
	totalvialcraftcost += bronze_craft_value*n_missing_bronzes
	
	n_missing_silvers = 0
	set_silvers = [x for x in mysetcardlist if 'silver' in x]
	for i in range(len(set_silvers)):
		thissilver = set_silvers[i]
		n_missing_silvers += max(3 - mycollection[thissilver], 0)
	
	totalvialcraftcost += silver_craft_value*n_missing_silvers
	
	n_missing_golds = 0
	set_golds = [x for x in mysetcardlist if 'gold' in x]
	for i in range(len(set_golds)):
		thisgold = set_golds[i]
		n_missing_golds += max(3 - mycollection[thisgold], 0)
	
	totalvialcraftcost += gold_craft_value*n_missing_golds
	
	n_missing_legendaries = 0
	set_legendaries = [x for x in mysetcardlist if 'legendary' in x]
	for i in range(len(set_legendaries)):
		thislegendary = set_legendaries[i]
		if use_1x_legendaries_limit:
			n_missing_legendaries += max(1 - mycollection[thislegendary], 0) ##use this if you're OK with just 1x of each legendary
		else:
			n_missing_legendaries += max(3 - mycollection[thislegendary], 0) ##use this for 3x everything
	
	totalvialcraftcost += legendary_craft_value*n_missing_legendaries
	
	return totalvialcraftcost

#calculateCollectionVialCompletionCost(mycollection, cardlist_ie) #213390

def calculateCollectionSmeltWorth_forSet(mycollection, mysetcardlist):
	total_vial_value = 0
	
	set_bronzes = [x for x in mysetcardlist if 'bronze' in x]
	for i in range(len(set_bronzes)):
		thisbronze = set_bronzes[i]
		total_vial_value += bronze_smelt_value*max(0, mycollection[thisbronze]-3)
	
	set_silvers = [x for x in mysetcardlist if 'silver' in x]
	for i in range(len(set_silvers)):
		thissilver = set_silvers[i]
		total_vial_value += silver_smelt_value*max(0, mycollection[thissilver]-3)
	
	set_golds = [x for x in mysetcardlist if 'gold' in x]
	for i in range(len(set_golds)):
		thisgold = set_golds[i]
		total_vial_value += gold_smelt_value*max(0, mycollection[thisgold]-3)
	
	set_legendaries = [x for x in mysetcardlist if 'legendary' in x]
	for i in range(len(set_legendaries)):
		thislegendary = set_legendaries[i]
		total_vial_value += legendary_smelt_value*max(0, mycollection[thislegendary]-3)
	
	return total_vial_value

def openPack(mysetcardlist, pity_counter):
	earned_cards = []
	for i in range(8):
		if i == 0 and pity_counter == 10:
			newcard = np.random.choice([x for x in mysetcardlist if 'legendary' in x])
		elif i < 7:
			rarity_roll = np.random.rand()
			if rarity_roll <= 0.675:
				newcard = np.random.choice([x for x in mysetcardlist if 'bronze' in x])
			elif rarity_roll > 0.675 and rarity_roll <= 0.925:
				newcard = np.random.choice([x for x in mysetcardlist if 'silver' in x])
			elif rarity_roll > 0.925 and rarity_roll <= 0.985:
				newcard = np.random.choice([x for x in mysetcardlist if 'gold' in x])
			elif rarity_roll > 0.985:
				newcard = np.random.choice([x for x in mysetcardlist if 'legendary' in x])
		elif i == 7:
			rarity_roll = np.random.rand()
			if rarity_roll <= 0.925:
				newcard = np.random.choice([x for x in mysetcardlist if 'silver' in x])
			elif rarity_roll > 0.925 and rarity_roll <= 0.985:
				newcard = np.random.choice([x for x in mysetcardlist if 'gold' in x])
			elif rarity_roll > 0.985:
				newcard = np.random.choice([x for x in mysetcardlist if 'legendary' in x])
		
		earned_cards.append(newcard)
	
	pack_has_legendary = len([x for x in earned_cards if 'legendary' in x]) > 0
	if not pack_has_legendary:
		pity_counter += 1
	else:
		pity_counter = 0
	
	return list([str(x) for x in earned_cards]), pity_counter

#newcards, pity_counter = openPack(cardlist_ie, 0)
#newcards, pity_counter = openPack(cardlist_ie, 10) #has a legendary, pity counter returns as 0

##now run a simulation on smelt value
# for i in range(100):
# 	newcards, pity_counter = openPack(cardlist_ie, 0)
# 	for x in newcards:
# 		mycollection[x] += 1
	
# 	print(calculateCollectionSmeltWorth_forSet(mycollection, cardlist_ie), 'smelt value')

##now we're ready to run the full simulation
def runSimulation(mysetcardlist):
	mycollection = Counter()
	pity_counter = 0
	n_opened_packs = 0
	cursmeltworth = calculateCollectionSmeltWorth_forSet(mycollection, mysetcardlist)
	curcraftcost = 99999
	while cursmeltworth < curcraftcost:
		newcards, pity_counter = openPack(mysetcardlist, pity_counter)
		for x in newcards:
			mycollection[x] += 1
		
		n_opened_packs += 1
		#if n_opened_packs % 10 == 0: #only run update every 10 packs
		cursmeltworth = calculateCollectionSmeltWorth_forSet(mycollection, mysetcardlist)
		#curcraftcost = calculateCollectionVialCompletionCost(mycollection, mysetcardlist, use_1x_legendaries_limit=True)
		curcraftcost = calculateCollectionVialCompletionCost(mycollection, mysetcardlist, use_1x_legendaries_limit=False)
		
		#print(n_opened_packs, 'packs, collection smelt worth:', cursmeltworth, 'vial cost to craft rest of cards needed:', curcraftcost)
	
	return n_opened_packs

packs_to_complete_tracker = []
for i in tqdm(range(1000)):
	packs_to_complete_tracker.append(runSimulation(cardlist_ho))
	#packs_to_complete_tracker.append(runSimulation(cardlist_ie))
	#packs_to_complete_tracker.append(runSimulation(cardlist_lr))

print('average packs needed:', np.mean(packs_to_complete_tracker))
print('min packs needed:', np.min(packs_to_complete_tracker))
print('max packs needed:', np.max(packs_to_complete_tracker))

'''
Heirs of the Omen: Same rarity counts as Infinity Evolved

For set Infinity Evolved: 

average packs needed: 255.723
min packs needed: 196
max packs needed: 302
Expected cost is about 5 crystal buys x 50 packs x $80 per buy = $400 to have 3x everything for Infinity Evolved.

For stopping after getting 1x of each legendary:
average packs needed: 137.096
min packs needed: 97
max packs needed: 182

Which is below $240 expected price.

For set Legends Rise:


Expected cost is about $640 to have 3x everything for Legends Rise.
average packs needed: 392.98
min packs needed: 320
max packs needed: 460

So ~400 = 8 x 50 packs = 8 x $80 = $640 to complete Legends Rise.

But with stopping after 1x of each legendary:
average packs needed: 245.378
min packs needed: 198
max packs needed: 296

Which cuts it from $640 to $400.
'''

'''
An easy rule of thumb on the price estimates is that legendaries will be the last thing you completely collect 3x of. The $80 package gets you 5500 crystals = 55 packs ~= 6 legendaries (not exact, slightly higher than the pity rate of 5.5). So each legendary costs you about $13 on average. So in order to see 3x of each you need somewhere from like 48-60 legendary pulls (not accounting for exact smelt value of all other cards). 50 x $13 = $650. But the reason it comes out to much less than this (about $400) is because of the smelt value of all duplicates across all rarities. But it does get you a pretty good rule of thumb that you're going to need something a little less than three times the count of legendaries per set, times 10 packs times which is ~$15 of crystals per 10 packs.
'''
