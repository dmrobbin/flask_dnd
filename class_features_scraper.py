from bs4 import BeautifulSoup
import requests
import re


list_of_classes=["Bard", "Barbarian", "Cleric", "Druid", "Fighter", "Monk", "Ranger", "Rogue", "Paladin", "Sorcerer", "Wizard", "Warlock"]

def get_tables():
	class_table={}


	for class_ in list_of_classes:
			html = requests.get('https://dnd5e.fandom.com/wiki/'+class_).text


			soup = BeautifulSoup(html, 'html.parser')

			content=soup.find('div', class_="mw-content-text")

			for link in content.find_all('a'):
			#link.replaceWithChildren()
				link.replaceWithChildren()

			table =content.table.extract()
			nav=content.nav.extract()
			
			class_table[class_]=[content]

	return class_table

def wrtite_to_text(class_table):
	for class_ in list_of_classes:
		with open("{}_features.txt".format(class_), "w+") as doc:
			for row in class_table[class_]:
				doc.write(str(row))

##Write to named files
