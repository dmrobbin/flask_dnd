from flask import Flask, render_template, request, redirect
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from flask_sqlalchemy import SQLAlchemy
from flask import request
from user import *
from werkzeug import secure_filename
import os
from flask import jsonify
import json
import random
import hashlib

import sqlite3
import pymysql

app=Flask(__name__)

##WILL NEED TO CHANGE WHEN UPLOADING
UPLOAD_FOLDER = '/Users/daryl.robbin/desktop/mine/static/images/'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
my_feat = Base.classes.DND_5E_FEAT
my_user = Base.classes.DND_USERS
my_image = Base.classes.DND_IMAGES
my_skills = Base.classes.DND_5E_SKILLS
my_slots=Base.classes.DND_5E_SLOTS
my_known=Base.classes.DND_5E_SPELLS_KNOWN
my_spells=Base.classes.DND_5E_SPELLS

current_user = User()
this_char = 0
bpar = "When I was a young boy My father took me into the city To see a marching band He said, son, when you grow up Would you be the savior of the broken The beaten, and the damned? He said, will you defeat them Your demons and all the non-believers? The plans that they have made? Because one day Ill leave you A phantom to lead you in the summer To join the black parade When I was a young boy My father took me into the city To see a marching band He said, son, when you grow up You will be the savior of the broken The beaten, and the damned?"

@app.route('/')
def character_list():
	if current_user.get_Id()==0:
		return redirect('/login')
	this_char=0
	characters = session.query(my_char).filter(my_char.user_id==current_user.get_Id()).all()
	return render_template('character_list.html', characters= characters)


@app.route('/info/<name>', methods=['POST', 'GET'])
def character_info(name):
	if current_user.get_Id()==0:
		return redirect('/login')

	character_query = session.query(my_char).filter(my_char.NAME == name and my_char.user_id==current_user.get_Id())
	character = session.query(my_char).filter(my_char.NAME == name and my_char.user_id==current_user.get_Id()).one_or_none()


	skills_query = session.query(my_skills).filter(my_skills.character_id == character.id and my_skills.user_id==current_user.get_Id())
	skills = skills_query.one_or_none()

	feats = session.query(my_feat).filter(my_feat.JOB == character.JOB).one_or_none()
	feats_dict = dict((col,getattr(feats, col)) for col in my_feat.__table__.columns.keys())

	slots = session.query(my_slots).filter(my_slots.JOB == character.JOB).one_or_none()
	slots_dict = dict((col,getattr(slots, col)) for col in my_slots.__table__.columns.keys())

	known = session.query(my_known).filter(my_known.JOB == character.JOB).one_or_none()
	known_dict = dict((col,getattr(known, col)) for col in my_known.__table__.columns.keys())

	spells = session.query(my_spells).filter(my_spells.CHARACTER_ID == character.id).all()

	this_char = character

	format_dict(known_dict)
	format_dict(slots_dict)
	format_dict(feats_dict)
	
	if request.method == 'POST' and request.form['remove'] == '1':
		character_query.delete()
		skills_query.delete()
		session.commit()
		return redirect('/')

	character = character_query.one_or_none()
	return render_template('character_info.html', character=character, skills = skills, feats=feats, feats_dict= feats_dict, slots_dict=slots_dict, known_dict=known_dict, spells=spells)


def format_dict(dict):
	del dict["id"]
	del dict["JOB"]
	dict[1] = dict.pop("LEVEL_1")
	dict[2] = dict.pop("LEVEL_2")
	dict[3] = dict.pop("LEVEL_3")
	dict[4] = dict.pop("LEVEL_4")
	dict[5] = dict.pop("LEVEL_5")
	dict[6] = dict.pop("LEVEL_6")
	dict[7] = dict.pop("LEVEL_7")
	dict[8] = dict.pop("LEVEL_8")
	dict[9] = dict.pop("LEVEL_9")
	dict[10] = dict.pop("LEVEL_10")
	dict[11] = dict.pop("LEVEL_11")
	dict[12] = dict.pop("LEVEL_12")
	dict[13] = dict.pop("LEVEL_13")
	dict[14] = dict.pop("LEVEL_14")
	dict[15] = dict.pop("LEVEL_15")
	dict[16] = dict.pop("LEVEL_16")
	dict[17] = dict.pop("LEVEL_17")
	dict[18] = dict.pop("LEVEL_18")
	dict[19] = dict.pop("LEVEL_19")
	dict[20] = dict.pop("LEVEL_20")


@app.route('/<name>/add_spell', methods=['POST', 'GET'])
def spell_add(name):
	character = session.query(my_char).filter(my_char.NAME == name and my_char.user_id==current_user.get_Id()).one_or_none()
	if current_user.get_Id()==0:
		return redirect('/login')

	if request.method == 'POST':

		session.add(my_spells(
			NAME=request.form['name'],
			LEVEL=int(request.form['level']),
			DESCRIPTION = request.form['description'],
			CHARACTER_ID = character.id,

		))

		session.commit()
		return redirect('/')
	else:
		return render_template('add_spell.html')

@app.route('/add', methods=['POST', 'GET'])
def character_add():

	if current_user.get_Id()==0:
		return redirect('/login')

	if request.method == 'POST':

		session.add(my_char(
			NAME=request.form['name'],
			LEVEL=int(request.form['level']),
			RACE = request.form['race'],
			JOB= request.form['job'],
			description= request.form['description'],
			STRENGTH = int(request.form['STRENGTH']),
			DEXTERITY = int(request.form['DEXTERITY']),
			CONSTITUTION = int(request.form['CONSTITUTION']),
			INTELLIGENCE = int(request.form['INTELLIGENCE']),
			WISDOM = int(request.form['WISDOM']),
			CHARISMA = int(request.form['CHARISMA']),
			user_id = current_user.get_Id(),

		))

		session.commit()

		character = session.query(my_char).filter(my_char.NAME == request.form['name'] and my_char.user_id==current_user.get_Id()).one_or_none()

		session.add(my_skills(
			user_id = current_user.get_Id(),
			character_id = character.id,
			Acrobatics = request.form.get('acrobatics'),
			Animal_Handling = request.form.get('animalhandling'),
			Arcana = request.form.get('arcana'),
			Athletics = request.form.get('athletics'),
			Deception = request.form.get('deception'),
			History = request.form.get('history'),
			Insight = request.form.get('insight'),
			Intimidation = request.form.get('intimidation'),
			Investigation = request.form.get('investigation'),
			Medicine = request.form.get('medicine'),
			Nature = request.form.get('nature'),
			Perception = request.form.get('perception'),
			Performance = request.form.get('performance'),
			Persuasion = request.form.get('persusaion'),
			Religion = request.form.get('religion'),
			Sleight_of_Hand = request.form.get('sleightofhand'),
			Stealth = request.form.get('stealth'),
			Survival = request.form.get('survivial'),

		))

		session.commit()

		return redirect('/')
	else:
		return render_template('character_add.html')

@app.route('/edit/<name>', methods=['POST', 'GET'])
def character_edit(name):
	if current_user.get_Id()==0:
		return redirect('/login')
	character = session.query(my_char).filter(my_char.NAME == name and my_char.user_id==current_user.get_Id()).one_or_none()
	skills_query = session.query(my_skills).filter(my_skills.character_id == character.id and my_skills.user_id==current_user.get_Id())
	skills = skills_query.one_or_none()	

	if request.method == 'POST' and request.form['edit'] == '1':

		if request.form['name']!='':
			character.NAME=request.form['name']
		if request.form['job'] !='':
			character.JOB=request.form['job']
		if request.form['race'] !='':
			character.RACE=request.form['race']
		if request.form['level'] !='':
			character.LEVEL=request.form['level']
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
		if request.form['description'] !='':
			character.description=request.form['description']
		#skills edit
		skills.Acrobatics = request.form.get('acrobatics'),
		skills.Animal_Handling = request.form.get('animalhandling'),
		skills.Arcana = request.form.get('arcana'),
		skills.Athletics = request.form.get('athletics'),
		skills.Deception = request.form.get('deception'),
		skills.History = request.form.get('history'),
		skills.Insight = request.form.get('insight'),
		skills.Intimidation = request.form.get('intimidation'),
		skills.Investigation = request.form.get('investigation'),
		skills.Medicine = request.form.get('medicine'),
		skills.Nature = request.form.get('nature'),
		skills.Perception = request.form.get('perception'),
		skills.Performance = request.form.get('performance'),
		skills.Persuasion = request.form.get('persuasion'),
		skills.Religion = request.form.get('religion'),
		skills.Sleight_of_Hand = request.form.get('sleightofhand'),
		skills.Stealth = request.form.get('stealth'),
		skills.Survival = request.form.get('survivial'),		

		session.commit()

		return redirect('/')

	return render_template('character_edit.html', character=character, skills=skills)


@app.route('/spell_edit/<name>', methods=['POST', 'GET'])
def spell_edit(name):
	if current_user.get_Id()==0:
		return redirect('/login')

	spell_query=session.query(my_spells).filter(my_spells.NAME == name and my_spells.CHARACTER_ID == this_char.id)
	spell=session.query(my_spells).filter(my_spells.NAME == name and my_spells.CHARACTER_ID == this_char.id).one_or_none()

	if request.method == 'POST' and request.form['edit'] == '1':
		if request.form['name']!='':
			spell.NAME=request.form['name']
		if request.form['level'] !='':
			spell.LEVEL=request.form['level']
		if request.form['description'] !='':
			spell.DESCRIPTION=request.form['description']
		session.commit()
		return redirect('/')

	return render_template('spell_edit.html', spell=spell)

@app.route('/spell_remover/<name>', methods = ['GET', 'POST'])
def remove_spell(name):

	if current_user.get_Id()==0:
		return redirect('/login')

	spell_query=session.query(my_spells).filter(my_spells.NAME == name and my_spells.CHARACTER_ID == this_char.id)
	spell=session.query(my_spells).filter(my_spells.NAME == name and my_spells.CHARACTER_ID == this_char.id).one_or_none()

	if request.method == 'POST':
		spell_query.delete()
		session.commit()
		return redirect('/')


@app.route('/class_details/<job>', methods=['GET'])
def class_details(job):

	feats = session.query(my_feat).filter(my_feat.JOB == job).one_or_none()
	feats_dict = dict((col,getattr(feats, col)) for col in my_feat.__table__.columns.keys())

	slots = session.query(my_slots).filter(my_slots.JOB ==job).one_or_none()
	slots_dict = dict((col,getattr(slots, col)) for col in my_slots.__table__.columns.keys())

	known = session.query(my_known).filter(my_known.JOB == job).one_or_none()
	known_dict = dict((col,getattr(known, col)) for col in my_known.__table__.columns.keys())

	format_dict(slots_dict)
	format_dict(feats_dict)
	format_dict(known_dict)

	return render_template('class_details.html', feats_dict=feats_dict, slots_dict=slots_dict, job=job, known_dict=known_dict)


@app.route('/create', methods=['POST', 'GET'])
def character_create():

	if current_user.get_Id()==0:
		return redirect('/login')

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
			description= request.form['description'],
			STRENGTH = int(request.form['STRENGTH']),
			DEXTERITY = int(request.form['DEXTERITY']),
			CONSTITUTION = int(request.form['CONSTITUTION']),
			INTELLIGENCE = int(request.form['INTELLIGENCE']),
			WISDOM = int(request.form['WISDOM']),
			CHARISMA = int(request.form['CHARISMA']),
			user_id = current_user.get_Id(),

		))

		try:
			session.commit()
		except:
			print("Error commiting changes to the dbmaster")

		character = session.query(my_char).filter(my_char.NAME == request.form['name'] and my_char.user_id==current_user.get_Id()).one_or_none()

		session.add(my_skills(
			user_id = current_user.get_Id(),
			character_id = character.id,
			Acrobatics = request.form.get('acrobatics'),
			Animal_Handling = request.form.get('animalhandling'),
			Arcana = request.form.get('arcana'),
			Athletics = request.form.get('athletics'),
			Deception = request.form.get('deception'),
			History = request.form.get('history'),
			Insight = request.form.get('insight'),
			Intimidation = request.form.get('intimidation'),
			Investigation = request.form.get('investigation'),
			Medicine = request.form.get('medicine'),
			Nature = request.form.get('nature'),
			Perception = request.form.get('perception'),
			Religion = request.form.get('religion'),
			Sleight_of_Hand = request.form.get('sleightofhand'),
			Stealth = request.form.get('stealth'),
			Survival = request.form.get('survivial'),

		))

		session.commit()

		return redirect('/')
	else:
		return render_template('character_create.html', rolls=rolls)

@app.route('/class_features', methods =['GET'])
def class_features():
	features = session.query(my_feat).all()
	return render_template('class_features.html', features= features)

@app.route('/registration', methods =['GET', 'POST'])
def registration():

	if request.method == 'POST':
		try:
			session.add(my_user(
				USER_NAME=request.form['user_name'],
				PASSWORD=hashbrowns(request.form['password']),
				))

			session.commit()
			return redirect('/login')
		except:
			return redirect('/invalid_registration')
	else:
		return render_template('registration.html')

def hashbrowns(password):
	h= hashlib.md5(password.encode())
	return h.hexdigest()

@app.route('/login', methods =['GET', 'POST'])
def login():
	
	if request.method == 'POST':
		#true username and password
		username = request.form['user_name']
		password = hashbrowns(request.form['password'])

		#validate against database
		try:
			this_user=session.query(my_user).filter(my_user.USER_NAME==username and my_user.PASSWORD==password).one_or_none()
			current_user.login(this_user.id, this_user.USER_NAME)
		except:
			return redirect('/invalid_login')
		

		return redirect('/')

	else:
		return render_template('login.html')

#hash function for protecting passwords
def hashbrowns(password):
	password = password + bpar
	h= hashlib.md5(password.encode())
	return h.hexdigest()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/logout')
def logout():
	current_user.logout()

	return redirect('/login')

@app.route('/invalid_login', methods =['GET'])
def invalid_login():
	
		return render_template('invalid_login.html')

@app.route('/invalid_registration', methods =['GET'])
def invalid_registration():
	
		return render_template('invalid_registration.html')

	
@app.route('/uploader/<name>', methods = ['GET', 'POST'])
def upload_files(name):
	if current_user.get_Id()==0:
		return redirect('/login')

	character = session.query(my_char).filter(my_char.NAME == name and my_char.user_id==current_user.get_Id()).one_or_none()

	if request.method == 'POST':
		file = request.files['file']
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		character.image=filename
		session.commit()
		return redirect('/')
		
if __name__ == '__main__':
   app.run(debug = True)
