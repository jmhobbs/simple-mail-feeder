# -*- coding: utf-8 -*-

import sqlite3
import util

connection = None
cursor = None

LOG_DEBUG='DEBUG'
LOG_WARNING='WARNING'
LOG_ERROR='ERROR'
LOG_FATAL='FATAL'

def init ( path ):
	global connection
	global cursor
	connection = sqlite3.connect( path )
	cursor = connection.cursor()

def log ( message, level=LOG_ERROR ):
	cursor.execute( "INSERT INTO [log] ( [logged], [level], [message] ) VALUES ( ?, ?, ? )", ( util.timestamp(), level, message ) )
	connection.commit()

def get_logs ( count=20, page=0, levels=(LOG_ERROR, LOG_FATAL) ):
	# TODO: Should be something like "is_iterable" right?
	if tuple == type( levels ) or list == type( levels ) or dict == type( levels ):
		type_string = 'WHERE ('
		for level in levels:
			type_string = type_string + ' [level] == ? OR'
			
		if 0 != len( levels ):
			type_string = type_string[:-2] + ")"
		else:
			type_string = ' '
	else:
		type_string = ' '
		levels = []

	type_string = "%s LIMIT %d,%d" % ( type_string, ( count * page ), count )
	
	result = cursor.execute( "SELECT * FROM [log] " + type_string , levels )
	
	logs = []
	for log in result:
		logs.append( log )

	return logs