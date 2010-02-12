# -*- coding: utf-8 -*-
import ConfigParser
import bcrypt
import web
from multiprocessing import Process
from smf import constants
import smf.feeder

# Load configuration variables
config = ConfigParser.RawConfigParser()
config.read( constants.DEFAULT_CONFIG )

# Set up web.py
web.config.debug = False

urls = (
	"/", "index",
	"/login", "login",
	"/logout", "logout",
	"/admin/feeder/start", "start_feeder",
	"/admin/feeder/stop", "stop_feeder"
)

app = web.application( urls, locals() )
session = web.session.Session( app, web.session.DiskStore('sessions'), initializer={ 'authenticated': False, 'flash': False, 'set_flash': False } )
render = web.template.render( 'templates/', base='layout', globals={'session': session} )
db = web.database( dbn='sqlite', db=config.get( 'Database', 'path' ) )

class index:
	def GET ( self ):
		if not session.authenticated:
			raise web.seeother( '/login' )
		else: 
			return render.index( feeder.is_alive() )

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
			session.set_flash = "Logged In"
			raise web.seeother( '/' )
		else:
			error = "Invalid Credentials"
			return render.login( error )

class logout:
	def GET( self ):
		session.kill()
		session.set_flash = "Logged Out"
		return render.login()

class start_feeder:
	def GET ( self ):
		global feeder
		if session.is_admin and not feeder.is_alive():
			feeder = Process( target=smf.feeder.run )
			feeder.daemon = True
			feeder.start()
			session.set_flash = "Feeder Started"
			raise web.seeother( '/' )

class stop_feeder:
	def GET ( self ):
		feeder.terminate()
		session.set_flash = "Feeder Stopped"
		raise web.seeother( '/' )

def flash_loadhook():
	if False != session.set_flash:
		session.flash = session.set_flash
		session.set_flash = False

def feeder_loadhook ():
	session.feeder = feeder.is_alive()

def flash_unloadhook():
	session.flash = False

app.add_processor( web.loadhook( flash_loadhook ) )
app.add_processor( web.loadhook( feeder_loadhook ) )
app.add_processor( web.unloadhook( flash_unloadhook ) )

feeder = Process( target=smf.feeder.run )
feeder.daemon = True
feeder.start()

app.run()