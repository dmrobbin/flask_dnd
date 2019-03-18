from flask import Flask, render_template, request, redirect
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from flask_sqlalchemy import SQLAlchemy

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

@app.route('/info/<name>', methods=['POST', 'GET'])
def character_info(name):
	character_query = session.query(my_char).filter(Base.classes.DND_5E_CHAR.NAME == name)

	if request.method == 'POST' and request.form['remove'] == '1':
		character_query.delete()
		session.commit()
		return redirect('/')

	character = character_query.one_or_none()
	return render_template('character_info.html', character=character)

if __name__ == '__main__':
	app.run(debug=True)
