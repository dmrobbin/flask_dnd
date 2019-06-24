from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
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
from flask_login import LoginManager
import flask_login
import flask
import class_table_scraper
import class_features_scraper
import re

app=Flask(__name__)
app.secret_key = 'burn my dread'

login_manager = flask_login.LoginManager()

login_manager.init_app(app)

##WILL NEED TO CHANGE WHEN UPLOADING
UPLOAD_FOLDER = '/home/ubuntu/flask_dnd/static/images/'

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
my_inventory=Base.classes.DND_5E_INVENTORY
my_multi=Base.classes.DND_5E_MULTI
my_bugs=Base.classes.DND_BUGS
my_race=Base.classes.DND_5E_RACES
my_sub=Base.classes.DND_5E_SUB
my_features=Base.classes.DND_5E_FEATURES
my_features_known=Base.classes.DND_5E_FEATURES_KNOWN
temp_tables=Base.classes.DND_CLASS_TABLES
temp_features=Base.classes.DND_CLASS_FEATURES

current_user = User()
this_char = 0

single_field_max=6000
min_field_len=6
max_hp=1000
min_hp=1
max_ac=50
min_ac=1
max_stat=30
min_stat=1

bpar = "When I was a young boy My father took me into the city To see a marching band He said, son, when you grow up Would you be the savior of the broken The beaten, and the damned? He said, will you defeat them Your demons and all the non-believers? The plans that they have made? Because one day Ill leave you A phantom to lead you in the summer To join the black parade When I was a young boy My father took me into the city To see a marching band He said, son, when you grow up You will be the savior of the broken The beaten, and the damned?"

SKILL_VALUES ={'Acrobatics' :'acrobatics', 'Animal_Handling': 'animalhandling', 'Arcana':'arcana', 'Athletics': 'athletics',
    'Deception':'deception', 'History':'history', 'Insight': 'insight', 'Intimidation': 'intimidation','Investigation':'investigation',
    'Medicine':'medicine', 'Nature':'nature','Perception':'perception', 'Performance': 'performance', 'Persuasion': 'persuasion',
    'Religion': 'religion', 'Sleight_of_Hand': 'sleightofhand', 'Stealth': 'stealth', 'Survival': 'survival',
    'Acrobatics_expert' :'acrobatics_expert', 'Animal_Handling_expert': 'animalhandling_expert', 'Arcana_expert':'arcana_expert', 'Athletics_expert': 'athletics_expert',
    'Deception_expert':'deception_expert', 'History_expert':'history_expert', 'Insight_expert': 'insight_expert', 'Intimidation_expert': 'intimidation_expert','Investigation_expert':'investigation_expert',
    'Medicine_expert':'medicine_expert', 'Nature_expert':'nature_expert','Perception_expert':'perception_expert', 'Performance_expert': 'performance_expert', 'Persuasion_expert': 'persuasion_expert',
    'Religion_expert': 'religion_expert', 'Sleight_of_Hand_expert': 'sleightofhand_expert', 'Stealth_expert': 'stealth_expert', 'Survival_expert': 'survival_expert'}

FEAT_LEVELS = ['LEVEL_1', 'LEVEL_2', 'LEVEL_3', 'LEVEL_4', 'LEVEL_5','LEVEL_6','LEVEL_7','LEVEL_8','LEVEL_9','LEVEL_10',
    'LEVEL_11', 'LEVEL_12', 'LEVEL_13', 'LEVEL_14', 'LEVEL_15','LEVEL_16','LEVEL_17','LEVEL_18','LEVEL_19','LEVEL_20',]

list_of_classes=["Bard", "Barbarian", "Cleric", "Druid", "Fighter", "Monk", "Ranger", "Rogue", "Paladin", "Sorcerer", "Wizard", "Warlock"]

INT_ATTRIBUTES={'STRENGTH': 'STRENGTH', 'DEXTERITY': 'DEXTERITY', 'CONSTITUTION':'CONSTITUTION', 'INTELLIGENCE': 'INTELLIGENCE', 'WISDOM': 'WISDOM', 'CHARISMA': 'CHARISMA',
'LEVEL': 'level', 'EXP': 'exp', 'HP':'hp', 'AC': 'ac'}

OTHER_ATTRIBUTES={'RACE':'race', 'description': 'description', 'NAME':'name', 'JOB':'job'}


class_table= class_table_scraper.get_tables()
feature_table= class_features_scraper.get_tables()

def hashbrowns(password):

    password = password + bpar
    h= hashlib.md5(password.encode())
    return h.hexdigest()

user = session.query(my_user).all()

ids={}
users={}
for item in user:
    users[str(item.USER_NAME)] = str(item.PASSWORD)

for item in user:
    ids[str(item.USER_NAME)] = item.id

admins={2}

###Create sub job dictionary###
sub_job_dict={}
option_sub_dict={}

jobs=session.query(my_feat).all()

def get_subs(job_name):

    return session.query(my_sub).filter(my_sub.JOB==job_name).all() 
    
for job in jobs:

    subs = get_subs(job.JOB)

    sub_list = []
    option_sub_string=""
    for sub in subs:
        sub_list.append(sub.SUB_JOB)

        option_sub_string+=('<option value = " '+sub.SUB_JOB + ' "> '+sub.SUB_JOB+'</option>')

    sub_job_dict[job.JOB]=sub_list
    option_sub_dict[job.JOB]=option_sub_string

###End create sub job dictiionary###

class User(flask_login.UserMixin):
    pass

def re_run_users():
    user = session.query(my_user).all()

    for item in user:
        users[str(item.USER_NAME)] = str(item.PASSWORD)

    for item in user:
        ids[str(item.USER_NAME)] = item.id

@login_manager.user_loader
def user_loader(user_name):

    if user_name not in users:
        return

    user = User()
    user.id = user_name
    return user

@login_manager.request_loader
def request_loader(request):

    user_name = request.form.get('user_name')
    if user_name not in users:
        return

    user = User()
    user.id = user_name

    try:
        user.is_authenticated = request.form['password'] == users[user_name]
    except:
        print("login attr err")

    return user

@app.route('/login', methods=['GET', 'POST'])
def login():

    errors = []

    re_run_users()

    if request.method == 'POST':
        user_name = request.form['user_name']
        password = request.form['password']
        hashed_password = hashbrowns(password)

        if session.query(my_user).filter(my_user.USER_NAME==user_name).one_or_none():
            
            re_run_users()

            if hashed_password == users[user_name]:
                user = User()
                user.id = user_name
                flask_login.login_user(user)
                return redirect('/?sort_on=id&is_reverse=True')
            else: 
                errors.append('Invalid Username or Password')
        else:
            errors.append('Username not found')

    return render_template('login.html', errors=errors)

@app.route('/logout')
def logout():

    flask_login.logout_user()
    return redirect('/login')

@login_manager.unauthorized_handler
def unauthorized_handler():

    return redirect('/login')

@app.route('/', methods=['GET'])
@flask_login.login_required
def character_list():

    admin =False

    this_char=0
    characters = session.query(my_char).filter(my_char.user_id==ids[flask_login.current_user.id]).all()
    characters.sort(key=lambda x: x.id, reverse=True)

    if len(characters)==1:
        character= session.query(my_char).filter(my_char.user_id==ids[flask_login.current_user.id]).one_or_none()
        return redirect(url_for('character_info',ida=character.id))
    if ids[flask_login.current_user.id] in admins:
        admin=True

    return render_template('character_list.html', characters= characters, admin=admin)

#######################
#####ADMIN POWERS######
#######################

@app.route('/admin')
@flask_login.login_required
def admin_list():

    if ids[flask_login.current_user.id] not in admins:
        return redirect('/?sort_on=id&is_reverse=True')

    this_char=0
    characters = session.query(my_char).all()
    users=session.query(my_user).all()
    return render_template('all_characters.html', characters= characters, users=users)

@app.route('/command')
@flask_login.login_required
def command():

    races=session.query(my_race).all()
    feats = session.query(my_feat).all()
    users=session.query(my_user).all()
    subs=session.query(my_sub).all()

    subs.sort(key=lambda x: x.JOB, reverse=False)

    if ids[flask_login.current_user.id] not in admins:
        return redirect('/?sort_on=id&is_reverse=True')

    return render_template('command.html', users=users, feats=feats, races=races, subs=subs)

@app.route('/edit_class/<job>', methods=['POST', 'GET'])
@flask_login.login_required
def edit_class(job):

    if ids[flask_login.current_user.id] not in admins:
        return redirect('/?sort_on=id&is_reverse=True')

    feats = session.query(my_feat).filter(my_feat.JOB == job).one_or_none()
    feats_dict = dict((col,getattr(feats, col)) for col in my_feat.__table__.columns.keys())

    format_dict(feats_dict)

    if request.method == 'POST' and request.form['edit'] == '1':

        for level in FEAT_LEVELS:
            temp=request.form[level]
            setattr(feats, level, temp)

        try:
            session.commit()
        except:
            session.rollback()

        return redirect('/command')

    return render_template('class_edit.html', feats_dict=feats_dict)

@app.route('/add_features', methods=['POST', 'GET'])
@flask_login.login_required
def add_features():

    if ids[flask_login.current_user.id] not in admins:
        return redirect('/?sort_on=id&is_reverse=True')

    if request.method == 'POST':

        session.add(my_features(
            NAME=request.form['name'],
            DESCRIPTION=request.form['description'],
        ))
        try:
            session.commit()
        except: 
            session.rollback()

        return redirect('/add_features')
    else:
        return render_template('add_feat.html')

@app.route('/add_race', methods=['POST', 'GET'])
@flask_login.login_required
def add_race():

    if ids[flask_login.current_user.id] not in admins:
        return redirect('/?sort_on=id&is_reverse=True')

    if request.method == 'POST':

        session.add(my_race(
            RACE=request.form['race'],
            STR_BONUS=int(request.form['str_bonus']),
            DEX_BONUS=int(request.form['dex_bonus']),
            CON_BONUS=int(request.form['con_bonus']),
            INT_BONUS=int(request.form['int_bonus']),
            WIS_BONUS=int(request.form['wis_bonus']),
            CHA_BONUS=int(request.form['cha_bonus']),
        ))
        try:
            session.commit()
        except: 
            session.rollback()

        return redirect('/command')
    else:
        return render_template('add_race.html')

@app.route('/add_sub', methods=['POST', 'GET'])
@flask_login.login_required
def add_sub():

    if ids[flask_login.current_user.id] not in admins:
        return redirect('/?sort_on=id&is_reverse=True')   

    feats=session.query(my_feat).all()
    
    if request.method=='POST':
        session.add(my_sub(
            SUB_JOB=request.form['sub_job'],
            JOB=request.form['job'],
            LEVEL_1=request.form['LEVEL_1'],
            LEVEL_2=request.form['LEVEL_2'],
            LEVEL_3=request.form['LEVEL_3'],
            LEVEL_4=request.form['LEVEL_4'],
            LEVEL_5=request.form['LEVEL_5'],
            LEVEL_6=request.form['LEVEL_6'],
            LEVEL_7=request.form['LEVEL_7'],
            LEVEL_8=request.form['LEVEL_8'],
            LEVEL_9=request.form['LEVEL_9'],
            LEVEL_10=request.form['LEVEL_10'],
            LEVEL_11=request.form['LEVEL_11'],
            LEVEL_12=request.form['LEVEL_12'],
            LEVEL_13=request.form['LEVEL_13'],
            LEVEL_14=request.form['LEVEL_14'],
            LEVEL_15=request.form['LEVEL_15'],
            LEVEL_16=request.form['LEVEL_16'],
            LEVEL_17=request.form['LEVEL_17'],
            LEVEL_18=request.form['LEVEL_18'],
            LEVEL_19=request.form['LEVEL_19'],
            LEVEL_20=request.form['LEVEL_20'],
            ))
        try:
            session.commit()
            return redirect('/command')
        except:
            session.rollback()

    return render_template('add_sub.html', feats=feats)

@app.route('/edit_sub/<sub>', methods=['POST', 'GET'])
@flask_login.login_required
def edit_sub(sub):

    if ids[flask_login.current_user.id] not in admins:
        return redirect('/?sort_on=id&is_reverse=True')

    subs = session.query(my_sub).filter(my_sub.SUB_JOB == sub).one_or_none()
    subs_dict = dict((col,getattr(subs, col)) for col in my_sub.__table__.columns.keys())
    feats=session.query(my_feat).all()

    del subs_dict["SUB_JOB"]
    format_dict(subs_dict)

    if request.method == 'POST' and request.form['edit'] == '1':
        subs.SUB_JOB=request.form['sub_job']
        subs.LEVEL_1=request.form['LEVEL_1'],
        subs.LEVEL_2=request.form['LEVEL_2'],
        subs.LEVEL_3=request.form['LEVEL_3'],
        subs.LEVEL_4=request.form['LEVEL_4'],
        subs.LEVEL_5=request.form['LEVEL_5'],
        subs.LEVEL_6=request.form['LEVEL_6'],
        subs.LEVEL_7=request.form['LEVEL_7'],
        subs.LEVEL_8=request.form['LEVEL_8'],
        subs.LEVEL_9=request.form['LEVEL_9'],
        subs.LEVEL_10=request.form['LEVEL_10'],
        subs.LEVEL_11=request.form['LEVEL_11'],
        subs.LEVEL_12=request.form['LEVEL_12'],
        subs.LEVEL_13=request.form['LEVEL_13'],
        subs.LEVEL_14=request.form['LEVEL_14'],
        subs.LEVEL_15=request.form['LEVEL_15'],
        subs.LEVEL_16=request.form['LEVEL_16'],
        subs.LEVEL_17=request.form['LEVEL_17'],
        subs.LEVEL_18=request.form['LEVEL_18'],
        subs.LEVEL_19=request.form['LEVEL_19'],
        subs.LEVEL_20=request.form['LEVEL_20'],

        try:
            session.commit()
        except:
            session.rollback()

        return redirect('/command')

    return render_template('sub_edit.html', subs_dict=subs_dict, feats=feats, subs=subs)

@app.route('/sub_remover/<sub>', methods = ['GET', 'POST'])
@flask_login.login_required
def remove_sub(sub):

    if ids[flask_login.current_user.id] not in admins:
        return redirect('/?sort_on=id&is_reverse=True')

    sub_query=session.query(my_sub).filter(my_sub.SUB_JOB == sub)

    if request.method == 'POST':
        sub_query.delete()

        try:
            session.commit()
        except:
            session.rollback()

        return redirect('/command')

@app.route('/edit_race/<race>', methods=['POST', 'GET'])
@flask_login.login_required
def edit_race(race):

    if ids[flask_login.current_user.id] not in admins:
        return redirect('/?sort_on=id&is_reverse=True')

    this_race=session.query(my_race).filter(my_race.RACE==race).one_or_none()

    if request.method == 'POST' and request.form['edit'] == '1':
        this_race.RACE=request.form['race'],
        this_race.STR_BONUS=int(request.form['str_bonus']),
        this_race.DEX_BONUS=int(request.form['dex_bonus']),
        this_race.CON_BONUS=int(request.form['con_bonus']),
        this_race.INT_BONUS=int(request.form['int_bonus']),
        this_race.WIS_BONUS=int(request.form['wis_bonus']),
        this_race.CHA_BONUS=int(request.form['cha_bonus']),
        try:
            session.commit()
        except:
            session.rollback()
        return redirect('/command')

    return render_template('edit_race.html', this_race=this_race)

@app.route('/race_remover/<race>', methods = ['GET', 'POST'])
@flask_login.login_required
def remove_race(race):

    if ids[flask_login.current_user.id] not in admins:
        return redirect('/?sort_on=id&is_reverse=True')

    race_query=session.query(my_race).filter(my_race.RACE == race)

    if request.method == 'POST':
        race_query.delete()

        try:
            session.commit()
        except:
            session.rollback()

        return redirect('/command')

@app.route('/bugs', methods =['GET', 'POST'])    
@flask_login.login_required
def bug_list():

    if ids[flask_login.current_user.id] in admins:
        bugs = session.query(my_bugs).all()
        return render_template('bugs_list.html', bugs= bugs)
    else: 
        return redirect('/?sort_on=id&is_reverse=True')

@app.route('/bug_remover/<ida>', methods=['GET','POST'])
@flask_login.login_required
def bug_remover(ida):

    if ids[flask_login.current_user.id] not in admins:
        return redirect('/?sort_on=id&is_reverse=True')

    bugs_query=session.query(my_bugs).filter(my_bugs.id==ida)
    bugs_query.delete()

    try:
        session.commit()
    except:
        sesison.rollback()

    return redirect('/command')

#######################
###END ADMIN POWERS####
#######################

@app.route('/info/<ida>', methods=['POST', 'GET'])
@flask_login.login_required
def character_info(ida):

    character_query = session.query(my_char).filter(my_char.id == ida and my_char.user_id==ids[flask_login.current_user.id])
    character = session.query(my_char).filter(my_char.id == ida and my_char.user_id==ids[flask_login.current_user.id]).one_or_none()

    if ids[flask_login.current_user.id] not in admins and ids[flask_login.current_user.id] != character.user_id:
        return redirect('/?sort_on=id&is_reverse=True')

    skills_query = session.query(my_skills).filter(my_skills.character_id == character.id and my_skills.user_id==ids[flask_login.current_user.id])
    skills = skills_query.one_or_none()

    feats = session.query(my_feat).filter(my_feat.JOB == character.JOB).one_or_none()
    feats_dict = dict((col,getattr(feats, col)) for col in my_feat.__table__.columns.keys())

    slots = session.query(my_slots).filter(my_slots.JOB == character.JOB).one_or_none()
    slots_dict = dict((col,getattr(slots, col)) for col in my_slots.__table__.columns.keys())

    known = session.query(my_known).filter(my_known.JOB == character.JOB).one_or_none()
    known_dict = dict((col,getattr(known, col)) for col in my_known.__table__.columns.keys())

    spells = session.query(my_spells).filter(my_spells.CHARACTER_ID == character.id).all()
    items = session.query(my_inventory).filter(my_inventory.CHARACTER_ID == character.id).all()

    multi_query=session.query(my_multi).filter(my_multi.CHARACTER_ID==character.id)
    multi = session.query(my_multi).filter(my_multi.CHARACTER_ID==character.id).first()

    features=session.query(my_features_known).filter(my_features_known.character_id==character.id).all()
    features_known=[]
    has_features=False

    if features:
        has_features=True
        for feat in features:
            features_known.append(session.query(my_features).filter(feat.feature_id==my_features.id).one_or_none())

    if character.SUB and character.SUB!='' and character.SUB!='None':
        sub=session.query(my_sub).filter(character.SUB==my_sub.SUB_JOB).one_or_none()
        sub_dict=dict((col,getattr(sub,col)) for col in my_sub.__table__.columns.keys())
        del sub_dict["SUB_JOB"]
        format_dict(sub_dict)
    else:
        sub_dict ={}

    if multi:
        multi_feats=session.query(my_feat).filter(my_feat.JOB == multi.JOB).one_or_none()
        multi_feats_dict = dict((col,getattr(multi_feats, col)) for col in my_feat.__table__.columns.keys())

        multi_slots = session.query(my_slots).filter(my_slots.JOB == multi.JOB).one_or_none()
        multi_slots_dict = dict((col,getattr(multi_slots, col)) for col in my_slots.__table__.columns.keys())

        multi_known = session.query(my_known).filter(my_known.JOB == multi.JOB).one_or_none()
        multi_known_dict = dict((col,getattr(multi_known, col)) for col in my_known.__table__.columns.keys())

        format_dict(multi_feats_dict)
        format_dict(multi_slots_dict)
        format_dict(multi_known_dict)

        if multi.SUB and multi.SUB!='' and multi.SUB!='None':
            sub=session.query(my_sub).filter(multi.SUB==my_sub.SUB_JOB).one_or_none()
            multi_sub_dict=dict((col,getattr(sub,col)) for col in my_sub.__table__.columns.keys())
            del multi_sub_dict["SUB_JOB"]
            format_dict(multi_sub_dict)
        else:
            multi_sub_dict ={}        

    else:
        multi_feats_dict={}
        multi_slots_dict={}
        multi_known_dict={}
        multi_sub_dict ={}  

    this_char = character

    format_dict(known_dict)
    format_dict(slots_dict)
    format_dict(feats_dict)

    if request.method == 'POST' and request.form['remove'] == '1':
        character_query.delete()
        skills_query.delete()
        multi_query.delete()
        try:
            session.commit()
        except:
            session.rollback()
        return redirect('/?sort_on=id&is_reverse=True')

    character = character_query.one_or_none()

    return render_template('character_info.html', character=character, skills = skills, 
        feats=feats, feats_dict= feats_dict, slots_dict=slots_dict, 
        known_dict=known_dict, spells=spells, items=items, multi=multi, multi_feats_dict=multi_feats_dict,
        multi_slots_dict=multi_slots_dict, multi_known_dict=multi_known_dict, sub_dict=sub_dict, multi_sub_dict=multi_sub_dict,
        features_known=features_known, has_features=has_features)

@app.route('/add_to_features_known/<ida>', methods=['POST', 'GET'])
@flask_login.login_required
def add_to_features_known(ida):

    character_query = session.query(my_char).filter(my_char.id == ida and my_char.user_id==ids[flask_login.current_user.id])
    character = session.query(my_char).filter(my_char.id == ida and my_char.user_id==ids[flask_login.current_user.id]).one_or_none()

    if ids[flask_login.current_user.id] not in admins and ids[flask_login.current_user.id] != character.user_id:
        return redirect('/?sort_on=id&is_reverse=True')

    features=session.query(my_features).all()

    if request.method == 'POST':

        session.add(my_features_known(
            user_id=character.user_id,
            character_id=character.id,
            feature_id=request.form['feat'],
            ))

        try:
            session.commit()
            return redirect(url_for('character_info', ida=character.id))

        except:
            session.rollback()
            print (" add to features session fail")
    return render_template('add_to_features.html', features=features)

@app.route('/remove_from_features_known/<ida>', methods=['POST', 'GET'])
@flask_login.login_required
def remove_from_features_known(ida):

    character=session.query(my_char).filter(my_char.id == ida and my_char.user_id==ids[flask_login.current_user.id]).one_or_none()

    features=session.query(my_features_known).filter(my_features_known.character_id==character.id).all()
    features_known=[]
    final_features={}

    for feat in features:
        this_known=session.query(my_features).filter(feat.feature_id==my_features.id).one_or_none()
        final_features[feat.id]=this_known.NAME
    
    if request.method == 'POST' and request.form['remove'] == '1':
        to_delete= int(request.form['feat']),

        if session.query(my_features_known).filter(my_features_known.id==to_delete and my_features_known.user_id==ids[flask_login.current_user.id]).first():
            feat_query=session.query(my_features_known).filter(my_features_known.id==to_delete)
            feat_query.delete()
        else:
            return "Nice try"
        try:
            session.commit()
            return redirect(url_for('character_info', ida=ida))
        except:
            session.rollback()

    return render_template('remove_from_features_known.html', final_features=final_features)

@app.route('/account', methods=['POST', 'GET'])
@flask_login.login_required
def account_info():

    user_query = session.query(my_user).filter(my_user.id==ids[flask_login.current_user.id])
    account= session.query(my_user).filter(my_user.id==ids[flask_login.current_user.id]).one_or_none()

    character_query= session.query(my_char).filter(my_char.user_id==ids[flask_login.current_user.id])
    characters = session.query(my_char).filter(my_char.user_id==ids[flask_login.current_user.id]).all()
    
    skills_query = session.query(my_skills).filter(my_skills.user_id==ids[flask_login.current_user.id])

    if request.method == 'POST' and request.form['remove'] == '1':
        user_query.delete()
        character_query.delete()
        skills_query.delete()

        try: 
            session.commit()
            re_run_users()
        except:
            session.rollback()

        return redirect('/logout')

    return render_template('account_info.html', account=account, characters=characters)

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

@app.route('/<ida>/add_spell', methods=['POST', 'GET'])
@flask_login.login_required
def spell_add(ida):

    character = session.query(my_char).filter(my_char.id == ida and my_char.user_id==ids[flask_login.current_user.id]).one_or_none()

    if request.method == 'POST':

        session.add(my_spells(
            NAME=request.form['name'],
            LEVEL=int(request.form['level']),
            DESCRIPTION = request.form['description'],
            CHARACTER_ID = character.id,

        ))
        try:
            session.commit()
        except: session.rollback()

        return redirect(url_for('character_info',ida=character.id))
    else:
        return render_template('add_spell.html')

@app.route('/add', methods=['POST', 'GET'])
@flask_login.login_required
def character_add():

    errors=[]
    races = session.query(my_race).all()

    valid_stat=True
    x=0
    y=0
    if request.method == 'POST':

        try:
            x+=int(request.form['level'])
            x+=int(request.form['hp'])
            x+=int(request.form['ac'])
            y+=int(request.form['STRENGTH'])
            y+=int(request.form['DEXTERITY'])
            y+=int(request.form['CONSTITUTION'])
            y+=int(request.form['INTELLIGENCE'])
            y+=int(request.form['WISDOM'])
            y+=int(request.form['CHARISMA'])

            if y>174 or y<6:
                valid_stat=False

            if int(request.form['level'])<20 and int(request.form['level'])>0:
                if int(request.form['hp'])>min_hp and int(request.form['hp'])<max_hp:
                    if int(request.form['ac'])>min_ac and int(request.form['ac'])<max_ac:
                        if valid_stat:
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
                                user_id = ids[flask_login.current_user.id],
                                HP=request.form['hp'],
                                AC=request.form['ac'],
                                STR_SAVE=request.form['STR_SAVE'],
                                DEX_SAVE=request.form['DEX_SAVE'],
                                CON_SAVE=request.form['CON_SAVE'],
                                INT_SAVE=request.form['INT_SAVE'],
                                WIS_SAVE=request.form['WIS_SAVE'],
                                CHA_SAVE=request.form['CHA_SAVE'],
                            ))
                            try:
                                session.commit()
                            except:
                                session.rollback()

                            character = session.query(my_char).filter(my_char.NAME == request.form['name'] and my_char.user_id==ids[flask_login.current_user.id]).one_or_none()
                            if request.form.get('job_multi')!='None':
                                session.add(my_multi(
                                    LEVEL=request.form.get('level_multi'),
                                    JOB = request.form.get('job_multi'),
                                    CHARACTER_ID = character.id,
                                ))

                            session.add(my_skills(
                                user_id = ids[flask_login.current_user.id],
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
                                Persuasion = request.form.get('persuasion'),
                                Religion = request.form.get('religion'),
                                Sleight_of_Hand = request.form.get('sleightofhand'),
                                Stealth = request.form.get('stealth'),
                                Survival = request.form.get('survival'),
                                ###Expertise###
                                Acrobatics_expert = request.form.get('acrobatics_expert'),
                                Animal_Handling_expert = request.form.get('animalhandling_expert'),
                                Arcana_expert = request.form.get('arcana_expert'),
                                Athletics_expert = request.form.get('athletics_expert'),
                                Deception_expert = request.form.get('deception_expert'),
                                History_expert = request.form.get('history_expert'),
                                Insight_expert = request.form.get('insight_expert'),
                                Intimidation_expert = request.form.get('intimidation_expert'),
                                Investigation_expert = request.form.get('investigation_expert'),
                                Medicine_expert = request.form.get('medicine_expert'),
                                Nature_expert = request.form.get('nature_expert'),
                                Perception_expert = request.form.get('perception_expert'),
                                Performance_expert = request.form.get('performance_expert'),
                                Persuasion_expert = request.form.get('persuasion_expert'),
                                Religion_expert = request.form.get('religion_expert'),
                                Sleight_of_Hand_expert = request.form.get('sleightofhand_expert'),
                                Stealth_expert = request.form.get('stealth_expert'),
                                Survival_expert = request.form.get('survival_expert'),
                            ))
                        else:
                            errors.append("Invalid Stat value")
                    else:
                        errors.append("Invalid AC value")
                else:
                    errors.append("Invalid HP value")
            else:
                errors.append("Invalid level")
        except:
            errors.append("Invalid field value")

        try:
            session.commit()
            return redirect(url_for('character_info',ida=character.id))
        except:
            session.rollback()

    return render_template('character_add.html', races=races, errors=errors)

def multi_edit(multi):

    if request.form.get('job_multi')!='Remove' or request.form.get('job_multi')!= 'None':
        multi.JOB = request.form.get('job_multi'),

        if int(request.form['level_multi'])>20 or int(request.form['level_multi'])<1:
            errors.append("Invalid multi class level")
        else:
            multi.LEVEL = request.form.get('level_multi'),
    else:
        multi_query=session.query(my_multi).filter(my_multi.CHARACTER_ID==character.id)
        multi_query.delete()

    if request.form['multi_sub']!='Remove' or request.form['multi_sub'] != '':
        multi.SUB=request.form['multi_sub'],
    else:
        multi.SUB=''

@app.route('/edit/<ida>', methods=['POST', 'GET'])
@flask_login.login_required
def character_edit(ida):

    races = session.query(my_race).all()
    character = session.query(my_char).filter(my_char.id == ida and my_char.user_id==ids[flask_login.current_user.id]).one_or_none()
    skills_query = session.query(my_skills).filter(my_skills.character_id == character.id and my_skills.user_id==ids[flask_login.current_user.id])
    skills = skills_query.one_or_none() 
    multi = session.query(my_multi).filter(my_multi.CHARACTER_ID==character.id).first()

    attributes=['STRENGTH', 'DEXTERITY', 'CONSTITUTION', 'INTELLIGENCE', 'WISDOM', 'CHARISMA', 'race', 'level', 'exp', 'hp', 'ac', 'description', 'name', 'job']

    multi_bool = False

    if multi:
        multi_subs=session.query(my_sub).filter(my_sub.JOB==multi.JOB).all()
        multi_bool=True
    else:
        multi_subs=None

    addR=0
    subs= session.query(my_sub).filter(my_sub.JOB==character.JOB).all()

    errors=[]

    if ids[flask_login.current_user.id] not in admins and ids[flask_login.current_user.id] != character.user_id:
        return redirect('/?sort_on=id&is_reverse=True')

    if request.method == 'POST' and request.form['edit'] == '1':
        
        if int(request.form['level'])<=20 and int(request.form['level'])>0:

            set_attribute(character)
            subtract_racial(character)

            try:
                if request.form['sub']!='Remove':
                    character.SUB=request.form['sub']
                else:
                    character.SUB=''
            except:
                session.rollback()
                errors.append("Error reading subclass information")

            saves_edit(character)
            skills_edit(character)
            
            if multi:
                multi_edit(multi)
                
            else:
                if request.form.get('job_multi')!= '' and request.form.get('level_multi')!='':
                    if int(request.form['level_multi'])<=20 or int(request.form['level_multi'])>=1:
                        session.add(my_multi(
                            JOB = request.form.get('job_multi'),
                            LEVEL=request.form.get('level_multi'),
                            CHARACTER_ID = character.id,
                        ))
                    else:
                        errors.append("Invalid multi class level")

            try:
                session.commit()

                add_racial(character)

                session.commit()
                return redirect(url_for('character_info',ida=character.id))
            except:
                session.rollback()
        else:
            errors.append("Invalid character Level")

    return render_template('character_edit.html', character=character, skills=skills, multi=multi, races=races, subs=subs, multi_subs=multi_subs,
        sub_job_dict=sub_job_dict, multi_bool=multi_bool, option_sub_dict=option_sub_dict, errors=errors)

def set_attribute(character):

    for key, value in INT_ATTRIBUTES.items():
        temp=int(request.form.get(value))
        setattr(character, key, temp)

    for key, value in OTHER_ATTRIBUTES.items():
        temp=request.form.get(value)
        setattr(character, key, temp)

def saves_edit(character):
    attribute_values=['STR_SAVE', 'DEX_SAVE', 'CON_SAVE', 'INT_SAVE', 'WIS_SAVE', 'CHA_SAVE']

    for value in attribute_values:
        temp=request.form.get(value)
        setattr(character, value, temp)

def skills_edit(character):
    import pdb
    pdb.set_trace()
    skills_query = session.query(my_skills).filter(my_skills.character_id == character.id and my_skills.user_id==ids[flask_login.current_user.id])
    skills = skills_query.one_or_none() 

    for key, value in SKILL_VALUES.items():
        temp=request.form.get(value)
        setattr(skills, key, temp)

@app.route('/spell_edit/<name>', methods=['POST', 'GET'])
@flask_login.login_required
def spell_edit(name):

    spell_query=session.query(my_spells).filter(my_spells.NAME == name and my_spells.CHARACTER_ID == this_char.id)
    spell=session.query(my_spells).filter(my_spells.NAME == name and my_spells.CHARACTER_ID == this_char.id).one_or_none()

    if request.method == 'POST' and request.form['edit'] == '1':
        if request.form['name']!='':
            spell.NAME=request.form['name']
        if request.form['level'] !='':
            spell.LEVEL=request.form['level']
        if request.form['description'] !='':
            spell.DESCRIPTION=request.form['description']
        try:
            session.commit()
        except:
            session.rollback()

        return redirect(url_for('character_info',ida=spell.CHARACTER_ID))

    return render_template('spell_edit.html', spell=spell)

@app.route('/spell_remover/<name>', methods = ['GET', 'POST'])
@flask_login.login_required
def remove_spell(name):

    spell_query=session.query(my_spells).filter(my_spells.NAME == name and my_spells.CHARACTER_ID == this_char.id)
    spell=session.query(my_spells).filter(my_spells.NAME == name and my_spells.CHARACTER_ID == this_char.id).one_or_none()

    if request.method == 'POST':
        spell_query.delete()

        try:
            session.commit()
        except:
            session.rollback()

        return redirect(url_for('character_info',ida=spell.CHARACTER_ID))

@app.route('/<ida>/add_item', methods=['POST', 'GET'])
@flask_login.login_required
def item_add(ida):

    character = session.query(my_char).filter(my_char.id == ida and my_char.user_id==ids[flask_login.current_user.id]).one_or_none()

    if ids[flask_login.current_user.id] != character.user_id:
        return redirect('/?sort_on=id&is_reverse=True')

    if request.method == 'POST':

        session.add(my_inventory(
            NAME=request.form['name'],
            DESCRIPTION = request.form['description'],
            CHARACTER_ID = character.id,
        ))

        try:
            session.commit()
        except:
            session.rollback()

        return redirect(url_for('character_info',ida=character.id))
    else:
        return render_template('add_item.html')

@app.route('/item_edit/<name>', methods=['POST', 'GET'])
@flask_login.login_required
def item_edit(name):

    item_query=session.query(my_inventory).filter(my_inventory.NAME == name and my_inventory.CHARACTER_ID == this_char.id)
    item=session.query(my_inventory).filter(my_inventory.NAME == name and my_inventory.CHARACTER_ID == this_char.id).one_or_none()

    if request.method == 'POST' and request.form['edit'] == '1':
        if request.form['name']!='':
            item.NAME=request.form['name']
        if request.form['description'] !='':
            item.DESCRIPTION=request.form['description']
        try:     
            session.commit()
        except:
            session.rollback()

        return redirect(url_for('character_info',ida=item.CHARACTER_ID))

    return render_template('item_edit.html', item=item)

@app.route('/item_remover/<name>', methods = ['GET', 'POST'])
@flask_login.login_required
def remove_item(name):

    item_query=session.query(my_inventory).filter(my_inventory.NAME == name and my_inventory.CHARACTER_ID == this_char.id)
    item=session.query(my_inventory).filter(my_inventory.NAME == name and my_inventory.CHARACTER_ID == this_char.id).one_or_none()

    if request.method == 'POST':
        item_query.delete()

        try:
            session.commit()
        except:
            session.rollback()

        return redirect(url_for('character_info',ida=item.CHARACTER_ID))

@app.route('/view_races', methods=['GET'])
def view_races():

    races=session.query(my_race).all()

    return render_template('view_races.html', races=races)

@app.route('/class_details/<job>', methods=['GET'])
def class_details(job):

    feats = session.query(my_feat).filter(my_feat.JOB == job).one_or_none()
    feats_dict = dict((col,getattr(feats, col)) for col in my_feat.__table__.columns.keys())

    slots = session.query(my_slots).filter(my_slots.JOB ==job).one_or_none()
    slots_dict = dict((col,getattr(slots, col)) for col in my_slots.__table__.columns.keys())

    known = session.query(my_known).filter(my_known.JOB == job).one_or_none()
    known_dict = dict((col,getattr(known, col)) for col in my_known.__table__.columns.keys())

    subs=session.query(my_sub).filter(my_sub.JOB==job).all()

    this_class_table=class_table[job][0]
    this_feature_table=feature_table[job]

    format_dict(slots_dict)
    format_dict(feats_dict)
    format_dict(known_dict)

    return render_template('class_details.html', feats_dict=feats_dict, slots_dict=slots_dict, job=job, known_dict=known_dict,
     subs=subs, this_class_table=this_class_table, this_feature_table=this_feature_table)

@app.route('/create', methods=['POST', 'GET'])
@flask_login.login_required
def character_create():

    x=0
    errors=[]
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

    races = session.query(my_race).all()

    if request.method == 'POST':
        try:
            x+=int(request.form['hp'])
            x+=int(request.form['ac'])
            
            if x<500 and x>2:
        
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
                    user_id = ids[flask_login.current_user.id],
                    HP=request.form['hp'],
                    AC=request.form['ac'],
                    STR_SAVE=request.form.get('STR_SAVE'),
                    DEX_SAVE=request.form.get('DEX_SAVE'),
                    CON_SAVE=request.form.get('CON_SAVE'),
                    INT_SAVE=request.form.get('INT_SAVE'),
                    WIS_SAVE=request.form.get('WIS_SAVE'),
                    CHA_SAVE=request.form.get('CHA_SAVE'),

                ))

                try:
                    print("tried to commit")
                    session.commit()
                except:
                    session.rollback()
                    print("/create Error commiting changes to the dbmaster")

                character = session.query(my_char).filter(my_char.NAME == request.form['name'] and my_char.user_id==ids[flask_login.current_user.id]).one_or_none()

                add_racial(character)
                if character.RACE=='Half Elf' or character.RACE=='Warforged Envoy':
                    if request.form.get('H_E_Strength'):
                        character.STRENGTH+=1
                    if request.form.get('H_E_Dexterity'):
                        character.DEXTERITY += 1
                    if request.form.get('H_E_Constitution'):
                        character.CONSTITUTION += 1
                    if request.form.get('H_E_Intelligence'):
                        character.INTELLIGENCE += 1
                    if request.form.get('H_E_Wisdom'):
                        character.WISDOM += 1
                    if request.form.get('H_E_Charisma'):
                        character.CHARISMA += 1

                session.add(my_skills(
                    user_id = ids[flask_login.current_user.id],
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
                    Persuasion = request.form.get('persuasion'),
                    Religion = request.form.get('religion'),
                    Sleight_of_Hand = request.form.get('sleightofhand'),
                    Stealth = request.form.get('stealth'),
                    Survival = request.form.get('survival'),
                    ###Expertise###
                    Acrobatics_expert = request.form.get('acrobatics_expert'),
                    Animal_Handling_expert = request.form.get('animalhandling_expert'),
                    Arcana_expert = request.form.get('arcana_expert'),
                    Athletics_expert = request.form.get('athletics_expert'),
                    Deception_expert = request.form.get('deception_expert'),
                    History_expert = request.form.get('history_expert'),
                    Insight_expert = request.form.get('insight_expert'),
                    Intimidation_expert = request.form.get('intimidation_expert'),
                    Investigation_expert = request.form.get('investigation_expert'),
                    Medicine_expert = request.form.get('medicine_expert'),
                    Nature_expert = request.form.get('nature_expert'),
                    Perception_expert = request.form.get('perception_expert'),
                    Performance_expert = request.form.get('performance_expert'),
                    Persuasion_expert = request.form.get('persuasion_expert'),
                    Religion_expert = request.form.get('religion_expert'),
                    Sleight_of_Hand_expert = request.form.get('sleightofhand_expert'),
                    Stealth_expert = request.form.get('stealth_expert'),
                    Survival_expert = request.form.get('survival_expert'),
                ))

                try:  
                    session.commit()
                except:
                    session.rollback()

                return redirect(url_for('character_info',ida=character.id))

            else:
                errors.append("Invalid HP or AC")
        except:
            errors.append("Invalid field value")

    return render_template('character_create.html', rolls=rolls, races=races, errors=errors)

def add_racial(character):
    print("Adding racials")
    race=session.query(my_race).filter(my_race.RACE==character.RACE).one_or_none()

    character.STRENGTH+=race.STR_BONUS
    character.DEXTERITY+=race.DEX_BONUS
    character.CONSTITUTION+=race.CON_BONUS
    character.INTELLIGENCE+=race.INT_BONUS
    character.WISDOM+=race.WIS_BONUS
    character.CHARISMA+=race.CHA_BONUS

def subtract_racial(character):

    race=session.query(my_race).filter(my_race.RACE==character.RACE).one_or_none()

    character.STRENGTH-=race.STR_BONUS
    character.DEXTERITY-=race.DEX_BONUS
    character.CONSTITUTION-=race.CON_BONUS
    character.INTELLIGENCE-=race.INT_BONUS
    character.WISDOM-=race.WIS_BONUS
    character.CHARISMA-=race.CHA_BONUS

@app.route('/class_features', methods =['GET'])
def class_features():

    features = session.query(my_feat).all()
    return render_template('class_features.html', features= features)

@app.route('/view_features', methods =['GET'])
def view_features():

    features = session.query(my_features).all()
    return render_template('view_features.html', features= features)

@app.route('/registration', methods =['GET', 'POST'])
def registration():

    errors =[]

    if request.method== 'POST':
        
        u_name = str(request.form['user_name'])
        p_word = str(request.form['password'])
        valid=True

        if len(u_name)<min_field_len or len(u_name)>single_field_max:
            errors.append("Username must be at least 6 characters")
            valid=False

        if len(p_word)<min_field_len or len(p_word)>single_field_max:
            errors.append("Password must be at least 6 characters")
            valid=False


        if valid:

            session.add(my_user(
                USER_NAME=request.form['user_name'],
                PASSWORD=hashbrowns(request.form['password']),
                ))
            try:
                session.commit()

                for item in user:
                    users[str(item.USER_NAME)] = str(item.PASSWORD)

                for item in user:
                    ids[str(item.USER_NAME)] = item.id
                return redirect('/login')

            except:
                session.rollback()
                errors.append("Invalid user_name or password entry")

    return render_template('registration.html', errors=errors)


def allowed_file(filename):

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploader/<ida>', methods = ['GET', 'POST'])
@flask_login.login_required
def upload_files(ida):
    
    character = session.query(my_char).filter(my_char.id == ida and my_char.user_id==ids[flask_login.current_user.id]).one_or_none()

    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        character.image=filename

        try:
            session.commit()
        except:
            session.rollback()

        return redirect('/?sort_on=id&is_reverse=True')
   
@app.route('/bug_report', methods = ['GET', 'POST'])
@flask_login.login_required
def bug_report():

    if request.method == 'POST':
        session.add(my_bugs(
            USER_ID=ids[flask_login.current_user.id],
            DESCRIPTION=request.form.get('description'),
            ))
        try:
            session.commit()
        except:
            session.rollback()

        return redirect('/?sort_on=id&is_reverse=True')
    else:
        return render_template('bug_report.html')

if __name__ == '__main__':
   app.run(debug = True)