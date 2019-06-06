from bs4 import BeautifulSoup
import requests
import re


list_of_classes=["Bard", "Barbarian", "Cleric", "Druid", "Fighter", "Monk", "Ranger", "Rogue", "Paladin", "Sorcerer", "Wizard", "Warlock"]

def get_tables():
	class_table={}
	
	for class_ in list_of_classes:
		html = requests.get('http://darylsite.com/'+class_+'_table.html').text

		soup = BeautifulSoup(html, 'html.parser')

		content =soup.find("table")

		for link in content.find_all('a'):
			#link.replaceWithChildren()
			if link['href'].startswith("/wiki"):
				try:
					link['href']= '#'+link['href'].split('#')[1]
				except:
					link.replaceWithChildren()


		content= content.find_all("tr")


		
		class_table[class_]=[content]
	return class_table

def wrtite_to_text(class_table):
	for class_ in list_of_classes:
		with open("{}_table.txt".format(class_), "w+") as doc:
			for row in class_table[class_]:
				doc.write(str(row))

##Write to named files


