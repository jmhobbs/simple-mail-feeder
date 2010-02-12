# -*- coding: utf-8 -*-
import ConfigParser
import bcrypt
import web
from smf import constants

# Load configuration variables
config = ConfigParser.RawConfigParser()
config.read( constants.DEFAULT_CONFIG )

# Set up web.py
web.config.debug = False

urls = (
	"/", "index",
	"/login", "login",
	"/logout", "logout"
)

app = web.application( urls, locals() )
session = web.session.Session( app, web.session.DiskStore('sessions'), initializer={ 'authenticated': False } )
render = web.template.render( 'templates/', base='layout' )
db = web.database( dbn='sqlite', db=config.get( 'Database', 'path' ) )

class index:
	def GET ( self ):
		if not session.authenticated:
			raise web.seeother( '/login' )
		else:
			return render.index()

class login:
	def GET( self ):
		if session.authenticated:
			raise web.seeother( '/' )
		return render.login( None )

	def POST( self ):
		i = web.input()
		res = db.select( 'users', { 'email': i.email }, where="email = $email", limit=1 )

		# See if we got anything from the db...
		try:
			user = res[0]
		except IndexError, e:
			error = "Invalid Credentials"
			return render.login( error )

		# See if the passwords match...
		if bcrypt.hashpw( i.password, user.password ) == user.password:
			session.authenticated = True
			session.user_id = user.id
			session.is_admin = user.is_admin
			raise web.seeother( '/' )
		else:
			error = "Invalid Credentials"
			return render.login( error )

class logout:
	def GET( self ):
		session.kill()
		error = "Logged Out"
		return render.login( error )

app.run()