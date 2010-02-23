# -*- coding: utf-8 -*-

import bcrypt

import database


class User:
	
	id = None
	is_admin = False
	email = ''
	password = ''
	
	@staticmethod
	def check_credentials ( email, password )
		res = database.cursor.execute( "SELECT [password], [id] FROM [users] WHERE [email] = ? LIMIT 0,1", ( email, ) )
		row = res.fetchone()
		if None == row:
			return False
		if bcrypt.hashpw( password, row[0] ) == row[0]:
			return row[1]
		else
			return False