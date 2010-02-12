# -*- coding: utf-8 -*-
import ConfigParser
import bcrypt
import sqlite3

from smf import constants

print "-" * 40
print "  Welcome to Simple Mail Feeder setup!"
print "-" * 40

# Load configuration variables
try:
	config = ConfigParser.RawConfigParser()
	if 0 == len( config.read( constants.DEFAULT_CONFIG ) ):
		print "Your configuration file doesn't exist. Let's build one.\n"
		while True:
			dbpath = raw_input( "Path to database: [smf.db3] " )
			if 0 == len( dbpath.strip() ):
				dbpath = 'smf.db3'
			break
		try:
			config.add_section( 'Database' )
			config.set( 'Database', 'path', dbpath )
			config.write( open( constants.DEFAULT_CONFIG, 'w' ) )
			print "Wrote your config file!"
		except Exception, e:
			print "Couldn't save your new config file, sorry!"
			print "Error:", e
			exit()
	
except Exception, e:
	print "Oops! Couldn't load your config file."
	print "Please set that up first."
	exit()

try:
	conn = sqlite3.connect( config.get( 'Database', 'path' ) )
	cursor = conn.cursor()
	res = cursor.execute( 'SELECT name FROM sqlite_master WHERE type="table"' )
	req_tables = { 'feeds': False, 'messages': False, 'subscriptions': False, 'users': False }
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
	print "\t1) Create new administrator"
	print
	option = raw_input( "What would you like to do? ")
	print
	if option == 'Q' or option == 'q':
		print "Goodbye!"
		exit()
	elif option == '1':
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
		cursor.execute( 'INSERT INTO users (is_admin, email, password) VALUES (?,?,?)', ( True, email, hashed ) );
		conn.commit()
		print
		print "Added administrative user."
	else:
		print "Invalid Option"
	print