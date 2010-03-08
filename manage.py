# -*- coding: utf-8 -*-
import ConfigParser
import bcrypt
import sqlite3

from smf import constants

def add_user( admin ):
	while True:
		email = raw_input( "E-Mail: " )
		if 0 == len( email.strip() ):
			print
			print "You must enter an email."
			print
		else:
			break
	while True:
		password = raw_input( "Password: " )
		if 0 == len( password.strip() ):
			print
			print "You must enter a password."
			print
		else:
			break
	hashed = bcrypt.hashpw( password, bcrypt.gensalt() )
	cursor.execute( 'INSERT INTO users (is_admin, email, password) VALUES (?,?,?)', ( admin, email, hashed ) );
	conn.commit()

print "-" * 40
print "  Welcome to Simple Mail Feeder setup!"
print "-" * 40

try:
	conn = sqlite3.connect( 'smf.db3' )
	cursor = conn.cursor()
	res = cursor.execute( 'SELECT name FROM sqlite_master WHERE type="table"' )
	req_tables = { 'feeds': False, 'stories': False, 'subscriptions': False, 'users': False, 'log': False }
	for row in res:
		if row[0] in req_tables.keys():
			req_tables[row[0]] = True
	for key,value in req_tables.items():
		if not value:
			print
			print "You are missing some tables in your database."
			print "You can not continue with an incomplete database."
			print "Rebuilding the database should not lose any existing data."
			print
			rebuild = raw_input( "Would you like to rebuild it? [y/N] " )
			if rebuild != 'y' and rebuild != 'Y':
				print "Ok, bailing out."
				exit()
			print "Rebuilding...",
			try:
				sqlfp = open( 'schema.sql', 'r' )
				sql = sqlfp.read()
				sqlfp.close()
				cursor.executescript( sql );
				print "Done!"
				break # Exit the for loop
			except Exception, e:
				print "Could not rebuild your database!"
				print "Error:", e
				exit()
except Exception, e:
	print "Error connecting to your database:", e
	exit()

while True:
	print "-" * 40
	print "Options:"
	print "\tq) Quit"
	print "\t1) Create admin user"
	print "\t2) Create normal user"
	print
	option = raw_input( "What would you like to do? ")
	print
	if option == 'Q' or option == 'q':
		print "Goodbye!"
		exit()
	elif option == '1':
		add_user( True )
		print
		print "Added admin user."
	elif option == '2':
		add_user( False )
		print
		print "Added normal user."
	else:
		print "Invalid Option"
	print