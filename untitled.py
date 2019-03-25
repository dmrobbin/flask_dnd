#!/usr/bin/env python

#!/usr/bin/python3

import pymysql

confirm = input("Would you like to reset the image database???")
if confirm == 'yes':
	# Open database connection
	db = pymysql.connect(host='ls-83b76412cfb19ce97b259074e362e7e2605c6a71.cmkceejlkolu.us-west-2.rds.amazonaws.com',
	                             user='dbmasteruser',
	                             password='P>wL5SB-;?ak&]U]xin47ZOy+|1&xml7',
	                             db='dbmaster')

	# prepare a cursor object using cursor() method
	cursor = db.cursor()

	# Drop table if it already exist using execute() method.
	cursor.execute("DROP TABLE IF EXISTS DND_IMAGES")

	# Create table as per requirement
	sql = """CREATE TABLE DND_IMAGES (
	   file_name CHAR(40) NOT NULL UNIQUE,
	   user_id INT NOT NULL,
	   character_id INT NOT NULL
	   )"""

	cursor.execute(sql)
	# disconnect from server


	db.close()
else:
	print ("did not reset table")