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
	cursor.execute( "INSERT INTO [log] ( [logged], [type], [message] ) VALUES ( ?, ?, ? )", ( util.timestamp(), level, message ) )
	connection.commit()