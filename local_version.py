from flask import Flask, render_template, request, redirect
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

app=Flask(__name__)
app.secret_key = 'burn my dread'

login_manager = flask_login.LoginManager()

login_manager.init_app(app)

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
my_inventory=Base.classes.DND_5E_INVENTORY
my_multi=Base.classes.DND_5E_MULTI

current_user = User()
this_char = 0

bpar = "When I was a young boy My father took me into the city To see a marching band He said, son, when you grow up Would you be the savior of the broken The beaten, and the damned? He said, will you defeat them Your demons and all the non-believers? The plans that they have made? Because one day Ill leave you A phantom to lead you in the summer To join the black parade When I was a young boy My father took me into the city To see a marching band He said, son, when you grow up You will be the savior of the broken The beaten, and the damned?"

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

class User(flask_login.UserMixin):
    pass

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

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['password'] == users[user_name]

    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return render_template('login.html')

    user_name = request.form['user_name']

    try:
        users[user_name]
    except:
        return redirect('/invalid_login')

    if hashbrowns(flask.request.form['password']) == users[user_name]:
        user = User()
        user.id = user_name
        flask_login.login_user(user)
        return redirect('/')

    return redirect('/invalid_login')

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect('/login')

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect('/login')

@app.route('/')
@flask_login.login_required
def character_list():

    this_char=0
    characters = session.query(my_char).filter(my_char.user_id==ids[flask_login.current_user.id]).all()
    return render_template('character_list.html', characters= characters)

@app.route('/info/<ida>', methods=['POST', 'GET'])
@flask_login.login_required
def character_info(ida):

    character_query = session.query(my_char).filter(my_char.id == ida and my_char.user_id==ids[flask_login.current_user.id])
    character = session.query(my_char).filter(my_char.id == ida and my_char.user_id==ids[flask_login.current_user.id]).one_or_none()

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
    else:
        multi_feats_dict={}
        multi_slots_dict={}
        multi_known_dict={}

    this_char = character

    format_dict(known_dict)
    format_dict(slots_dict)
    format_dict(feats_dict)

    if request.method == 'POST' and request.form['remove'] == '1':
        character_query.delete()
        skills_query.delete()
        multi_query.delete()
        session.commit()
        return redirect('/')

    character = character_query.one_or_none()
    return render_template('character_info.html', character=character, skills = skills, 
        feats=feats, feats_dict= feats_dict, slots_dict=slots_dict, 
        known_dict=known_dict, spells=spells, items=items, multi=multi, multi_feats_dict=multi_feats_dict,
        multi_slots_dict=multi_slots_dict, multi_known_dict=multi_known_dict)

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

        session.commit()
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

        session.commit()
        return redirect('/')
    else:
        return render_template('add_spell.html')

@app.route('/add', methods=['POST', 'GET'])
@flask_login.login_required
def character_add():

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
            user_id = ids[flask_login.current_user.id],
            HP=request.form['hp'],
            AC=request.form['ac'],
        ))

        session.commit()

        character = session.query(my_char).filter(my_char.NAME == request.form['name'] and my_char.user_id==ids[flask_login.current_user.id]).one_or_none()

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

        session.commit()

        return redirect('/')
    else:
        return render_template('character_add.html')

@app.route('/edit/<ida>', methods=['POST', 'GET'])
@flask_login.login_required
def character_edit(ida):
    
    character = session.query(my_char).filter(my_char.id == ida and my_char.user_id==ids[flask_login.current_user.id]).one_or_none()
    skills_query = session.query(my_skills).filter(my_skills.character_id == character.id and my_skills.user_id==ids[flask_login.current_user.id])
    skills = skills_query.one_or_none() 
    multi = session.query(my_multi).filter(my_multi.CHARACTER_ID==character.id).first()

    if request.method == 'POST' and request.form['edit'] == '1':

        if request.form['name']!='':
            character.NAME=request.form['name']
        if request.form['job'] !='':
            character.JOB=request.form['job']
        if request.form['race'] !='':
            character.RACE=request.form['race']
        if request.form['level'] !='':
            character.LEVEL=request.form['level']
        if request.form['hp'] !='':
            character.HP=request.form['hp']
        if request.form['ac'] !='':
            character.AC=request.form['ac']
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
        skills.Survival = request.form.get('survival'),        
        #expert edit
        skills.Acrobatics_expert = request.form.get('acrobatics_expert'),
        skills.Animal_Handling_expert = request.form.get('animalhandling_expert'),
        skills.Arcana_expert = request.form.get('arcana_expert'),
        skills.Athletics_expert = request.form.get('athletics_expert'),
        skills.Deception_expert = request.form.get('deception_expert'),
        skills.History_expert = request.form.get('history_expert'),
        skills.Insight_expert = request.form.get('insight_expert'),
        skills.Intimidation_expert = request.form.get('intimidation_expert'),
        skills.Investigation_expert = request.form.get('investigation_expert'),
        skills.Medicine_expert = request.form.get('medicine_expert'),
        skills.Nature_expert = request.form.get('nature_expert'),
        skills.Perception_expert = request.form.get('perception_expert'),
        skills.Performance_expert = request.form.get('performance_expert'),
        skills.Persuasion_expert = request.form.get('persuasion_expert'),
        skills.Religion_expert = request.form.get('religion_expert'),
        skills.Sleight_of_Hand_expert = request.form.get('sleightofhand_expert'),
        skills.Stealth_expert = request.form.get('stealth_expert'),
        skills.Survival_expert = request.form.get('survival_expert'),
        
        #if multi exists
        if multi:
            if request.form.get('job_multi')!='Remove':
                if request.form.get('job_multi')!= 'None':
                    multi.JOB = request.form.get('job_multi'),
                if request.form.get('level_multi')!='':
                    multi.LEVEL = request.form.get('level_multi'),
            else:
                multi_query=session.query(my_multi).filter(my_multi.CHARACTER_ID==character.id)
                multi_query.delete()
        else:
            if request.form.get('job_multi')!= '' and request.form.get('level_multi')!='':
                session.add(my_multi(
                    LEVEL=request.form.get('level_multi'),
                    JOB = request.form.get('job_multi'),
                    CHARACTER_ID = character.id,
                ))

        session.commit()

        return redirect('/')

    return render_template('character_edit.html', character=character, skills=skills, multi=multi)

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
        session.commit()
        return redirect('/')

    return render_template('spell_edit.html', spell=spell)

@app.route('/spell_remover/<name>', methods = ['GET', 'POST'])
@flask_login.login_required
def remove_spell(name):

    spell_query=session.query(my_spells).filter(my_spells.NAME == name and my_spells.CHARACTER_ID == this_char.id)
    spell=session.query(my_spells).filter(my_spells.NAME == name and my_spells.CHARACTER_ID == this_char.id).one_or_none()

    if request.method == 'POST':
        spell_query.delete()
        session.commit()
        return redirect('/')

@app.route('/<ida>/add_item', methods=['POST', 'GET'])
@flask_login.login_required
def item_add(ida):

    character = session.query(my_char).filter(my_char.id == ida and my_char.user_id==ids[flask_login.current_user.id]).one_or_none()

    if request.method == 'POST':

        session.add(my_inventory(
            NAME=request.form['name'],
            DESCRIPTION = request.form['description'],
            CHARACTER_ID = character.id,
        ))

        session.commit()
        return redirect('/')
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
        session.commit()
        return redirect('/')

    return render_template('item_edit.html', item=item)

@app.route('/item_remover/<name>', methods = ['GET', 'POST'])
@flask_login.login_required
def remove_item(name):

    item_query=session.query(my_inventory).filter(my_inventory.NAME == name and my_inventory.CHARACTER_ID == this_char.id)
    item=session.query(my_inventory).filter(my_inventory.NAME == name and my_inventory.CHARACTER_ID == this_char.id).one_or_none()

    if request.method == 'POST':
        item_query.delete()
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
@flask_login.login_required
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
        ))

        try:
            session.commit()
        except:
            print("Error commiting changes to the dbmaster")

        character = session.query(my_char).filter(my_char.NAME == request.form['name'] and my_char.user_id==ids[flask_login.current_user.id]).one_or_none()

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
            user = session.query(my_user).all()

            for item in user:
                users[str(item.USER_NAME)] = str(item.PASSWORD)

            for item in user:
                ids[str(item.USER_NAME)] = item.id   

            return redirect('/login')
        except:
            return redirect('/invalid_registration')
    else:
        return render_template('registration.html')

@app.route('/invalid_login', methods =['GET'])
def invalid_login():
    
        return render_template('invalid_login.html')

@app.route('/invalid_registration', methods =['GET'])
def invalid_registration():
    
        return render_template('invalid_registration.html')

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
        session.commit()
        return redirect('/')
        
if __name__ == '__main__':
   app.run(debug = True)