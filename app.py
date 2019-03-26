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

current_user = User()

bpar = "When I was a young boy My father took me into the city To see a marching band He said, son, when you grow up Would you be the savior of the broken The beaten, and the damned? He said, will you defeat them Your demons and all the non-believers? The plans that they have made? Because one day Ill leave you A phantom to lead you in the summer To join the black parade When I was a young boy My father took me into the city To see a marching band He said, son, when you grow up You will be the savior of the broken The beaten, and the damned?"

@app.route('/')
def character_list():
	if current_user.get_Id()==0:
		return redirect('/login')

	characters = session.query(my_char).filter(my_char.user_id==current_user.get_Id()).all()
	return render_template('character_list.html', characters= characters)

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

		return redirect('/')
	else:
		return render_template('character_add.html')

@app.route('/edit/<name>', methods=['POST', 'GET'])
def character_edit(name):
	if current_user.get_Id()==0:
		return redirect('/login')
	character = session.query(my_char).filter(my_char.NAME == name and my_char.user_id==current_user.get_Id()).one_or_none()


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
		if request.form['description'] !='':
			character.description=request.form['description']


		session.commit()
		return redirect('/')

	return render_template('character_edit.html', character=character)


@app.route('/info/<name>', methods=['POST', 'GET'])
def character_info(name):
	if current_user.get_Id()==0:
		return redirect('/login')
	character_query = session.query(my_char).filter(my_char.NAME == name and my_char.user_id==current_user.get_Id())

	if request.method == 'POST' and request.form['remove'] == '1':
		character_query.delete()
		session.commit()
		return redirect('/')

	character = character_query.one_or_none()
	return render_template('character_info.html', character=character)


@app.route('/class_details/<job>', methods=['GET'])
def class_details(job):
	features_query = session.query(my_feat).filter(my_feat.JOB == job)
	feature = features_query.one_or_none()
	return render_template('class_details.html', feature=feature)


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

### upload test

@app.route('/upload/<name>')
def upload_file(name):
	if current_user.get_Id()==0:
		return redirect('/login')
	character = session.query(my_char).filter(my_char.NAME == name and my_char.user_id==current_user.get_Id()).one_or_none()
	return render_template('upload.html', character = character)
	
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

'''@app.route('/edit/<name>', methods=['POST', 'GET'])
def character_edit(name):
	character = session.query(my_char).filter(my_char.NAME == name and my_char.user_id==current_user.get_Id()).one_or_none()


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
		if request.form['description'] !='':
			character.description=request.form['description']


		session.commit()
		return redirect('/')

	return render_template('character_edit.html', character=character)  '''
### end upload test

if __name__ == '__main__':
	app.run(debug=True)
