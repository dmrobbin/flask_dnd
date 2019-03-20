from flask import Flask, render_template, request, redirect
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from flask_sqlalchemy import SQLAlchemy
from flask import request
import random

import sqlite3
import pymysql

app=Flask(__name__)

#
# Database configuration
#

pymysql.install_as_MySQLdb()

engine = create_engine('mysql://dbmasteruser:P>wL5SB-;?ak&]U]xin47ZOy+|1&xml7@ls-83b76412cfb19ce97b259074e362e7e2605c6a71.cmkceejlkolu.us-west-2.rds.amazonaws.com:3306/dbmaster')

session = Session(bind=engine)

Base = automap_base()
Base.prepare(engine,reflect = True)
Base.metadata.create_all(engine)

my_char = Base.classes.DND_5E_CHAR

@app.route('/')
def character_list():
	characters = session.query(my_char).all()
	return render_template('character_list.html', characters= characters)

@app.route('/add', methods=['POST', 'GET'])
def character_add():
	character_query = session.query(my_char).all()
	if request.method == 'POST':

		session.add(my_char(
			NAME=request.form['name'],
			LEVEL=int(request.form['level']),
			RACE = request.form['race'],
			JOB= request.form['job'],
			STRENGTH = int(request.form['STRENGTH']),
			DEXTERITY = int(request.form['DEXTERITY']),
			CONSTITUTION = int(request.form['CONSTITUTION']),
			INTELLIGENCE = int(request.form['INTELLIGENCE']),
			WISDOM = int(request.form['WISDOM']),
			CHARISMA = int(request.form['CHARISMA']),
		))
		session.commit()

		return redirect('/')
	else:
		return render_template('character_add.html')

@app.route('/edit/<name>', methods=['POST', 'GET'])
def character_edit(name):
	character = session.query(my_char).filter(my_char.NAME == name).one_or_none()

	if request.method == 'POST' and request.form['edit'] == '1':

		if request.form['name']!='':
			character.NAME=request.form['name']
		if request.form['job'] !='':
			character.JOB=request.form['job']
		if request.form['race'] !='':
			character.RACE=request.form['race']
		if request.form['STRENGTH'] !='':
			character.STRENGTH=request.form['STRENGTH']
		if request.form['DEXTERITY'] !='':
			character.DEXTERITY=request.form['DEXTERITY']
		if request.form['CONSTITUTION'] !='':
			character.CONSTITUTION=request.form['CONSTITUTION']
		if request.form['INTELLIGENCE'] !='':
			character.INTELLIGENCE=request.form['INTELLIGENCE']
		if request.form['WISDOM'] !='':
			character.WISDOM=request.form['WISDOM']
		if request.form['CHARISMA'] !='':
			character.CHARISMA=request.form['CHARISMA']

		session.commit()
		return redirect('/')

	return render_template('character_edit.html', character=character)


@app.route('/info/<name>', methods=['POST', 'GET'])
def character_info(name):
	character_query = session.query(my_char).filter(my_char.NAME == name)

	if request.method == 'POST' and request.form['remove'] == '1':
		character_query.delete()
		session.commit()
		return redirect('/')

	character = character_query.one_or_none()
	return render_template('character_info.html', character=character)

#not finished
@app.route('/create', methods=['POST', 'GET'])
def character_create():
	rolls=[]
	#loop for each stat
	for x in range(6):
		dice=[]
		#roll 4d6
		for y in range(4):
			dice.append(random.randint(1, 6))

		#remove lowest dice
		dice.sort()
		dice.pop(0)
		sum=0
		for die in dice:
			sum+=die

		rolls.append(sum)

	rolls.sort(reverse=True)

	if request.method == 'POST':

		
		session.add(my_char(
			NAME=request.form['name'],
			LEVEL=1,
			RACE = request.form['race'],
			JOB= request.form['job'],
			STRENGTH = int(request.form['STRENGTH']),
			DEXTERITY = int(request.form['DEXTERITY']),
			CONSTITUTION = int(request.form['CONSTITUTION']),
			INTELLIGENCE = int(request.form['INTELLIGENCE']),
			WISDOM = int(request.form['WISDOM']),
			CHARISMA = int(request.form['CHARISMA']),

		))
		session.commit()

		return redirect('/')
	else:
		return render_template('character_create.html', rolls=rolls)



if __name__ == '__main__':
	app.run(debug=True)
