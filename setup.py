# -*- coding: utf-8 -*-

import bcrypt
password = ""

print "-" * 40
print "  Welcome to Simple Mail Feeder setup!"
print "-" * 40
print
print "First we need to set up your administrative user."
print "Please complete the prompts."
print

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

password = bcrypt.hashpw( password, bcrypt.gensalt() )
print password