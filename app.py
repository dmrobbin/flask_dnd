from flask import Flask, render_template, request, redirect
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base

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

# print('Available classes', Base.classes.keys())

@app.route('/')
def character_list():
	characters = session.query(Base.classes.DND_5E_CHAR).all()
	return render_template('character_list.html', characters= characters)


if __name__ == '__main__':
	app.run(debug=True)
