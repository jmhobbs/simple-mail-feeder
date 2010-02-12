# -*- coding: utf-8 -*-
from datetime import datetime
import time
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
	"/admin/feeder/stop", "stop_feeder",
	
	"/admin/feeds", "list_feeds",
	
	"/user/subscribe", "user_subscribe",
	"/user/unsubscribe/(.*)", "user_unsubscribe",
	"/user/subscriptions", "user_subscriptions"
)

app = web.application( urls, locals() )
session = web.session.Session( app, web.session.DiskStore('sessions'), initializer={ 'authenticated': False, 'user_id': 0, 'is_admin': False, 'flash': False, 'set_flash': False, 'error_flash': False, 'set_error_flash': False } )
render = web.template.render( 'views/', base='layout', globals={'session': session} )
db = web.database( dbn='sqlite', db=config.get( 'Database', 'path' ) )

class index:
	def GET ( self ):
		results = db.query( "SELECT COUNT(*) AS subscriptions FROM subscriptions WHERE user_id=$user_id", vars={ 'user_id': session.user_id } )
		return render.index( results[0].subscriptions )

####### Session Management #######

class login:
	def GET( self ):
		if session.authenticated:
			raise web.seeother( '/' )
		return render.login()

	def POST( self ):
		i = web.input()
		res = db.select( 'users', { 'email': i.email }, where="email = $email", limit=1 )

		# See if we got anything from the db...
		try:
			user = res[0]
		except IndexError, e:
			session.error_flash = "Invalid Credentials"
			return render.login()

		# See if the passwords match...
		if bcrypt.hashpw( i.password, user.password ) == user.password:
			session.authenticated = True
			session.user_id = user.id
			session.is_admin = user.is_admin
			session.set_flash = "Logged In"
			raise web.seeother( '/' )
		else:
			session.error_flash = "Invalid Credentials"
			return render.login()

class logout:
	def GET( self ):
		session.authenticated = False
		session.user_id = 0
		session.is_admin = False
		session.kill()
		session.flash = "Logged Out"
		return render.login()

####### Feeder Management #######

class start_feeder:
	def GET ( self ):
		global feeder
		if not feeder.is_alive():
			feeder = Process( target=smf.feeder.run )
			feeder.daemon = True
			feeder.start()
			session.set_flash = "Feeder Started"
		else:
			session.set_flash = "Feeder Already Running"
		raise web.seeother( '/' )

class stop_feeder:
	def GET ( self ):
		feeder.terminate()
		session.set_flash = "Feeder Stopped"
		raise web.seeother( '/' )

####### Feed Management #######

class list_feeds:
	def GET ( self ):
		# TODO: Detailed metrics here
		feeds = db.select( 'feeds' )
		return render.list_feeds( feeds )

####### Subscription Management #######

class user_subscribe:
	def POST ( self ):
		i = web.input()
		res = db.select( 'feeds', { 'url': i.url }, what="title,id", where="url = $url", limit=1 )
		try:
			match = res[0]
			feed_id = match.id
			title = match.title
		except IndexError, e:
			result = smf.feeder.new_feed( i.url )
			if dict == type( result ):
				now = time.strftime( '%Y-%m-%d %H:%M:%s', datetime.now().timetuple() )
				modified = time.strftime( '%Y-%m-%d %H:%M:%s', result['modified'] )
				feed_id = db.insert( 'feeds', title=result['title'], url=result['url'], description=result['description'], link=result['link'], added=now, checked=now, modified=modified, etag=result['etag'], interval=900 )
				title = result['title']
			else:
				session.set_error_flash = 'Error adding subscription: ' + result
				raise web.seeother( '/user/subscriptions' )

		db.insert( 'subscriptions', feed_id=feed_id, user_id=session.user_id )
		session.set_flash = 'Subscribed to  "' + title + '"'
		raise web.seeother( '/user/subscriptions' )

class user_unsubscribe:
	def GET ( self, feed_id ):
		db.query( "DELETE FROM subscriptions WHERE feed_id = $feed_id AND user_id = $user_id", vars={ 'feed_id': feed_id, 'user_id': session.user_id } )
		session.set_flash = 'Unsubscribed!'
		raise web.seeother( '/user/subscriptions' )

class user_subscriptions:
	def GET ( self ):
		subcount_results = db.query( "SELECT COUNT(*) AS subscriptions FROM subscriptions WHERE user_id=$user_id", vars={ 'user_id': session.user_id } )
		feed_results = db.query( "SELECT * FROM feeds WHERE id IN ( SELECT feed_id FROM subscriptions WHERE user_id = $user_id )", vars={ 'user_id': session.user_id } )
		return render.user_subscriptions( subcount_results[0].subscriptions, feed_results )

####### Pre/Post Hooks #######

def permission_loadhook ():
	no_auth_actions = ( '/login', '/logout' )
	if not session.authenticated and web.ctx.path not in no_auth_actions :
		raise web.seeother( '/login' )

	if not session.is_admin and "admin" == web.ctx.path[1:6]:
		# TODO: Log this here
		session.set_flash = "Permission denied. You are not an admin, you may not access: " + web.ctx.path
		raise web.seeother( '/' )

def flash_loadhook ():
	if False != session.set_flash:
		session.flash = session.set_flash
		session.set_flash = False
	if False != session.set_error_flash:
		session.error_flash = session.set_error_flash
		session.set_error_flash = False

def feeder_loadhook ():
	session.feeder = feeder.is_alive()

def flash_unloadhook ():
	session.flash = False
	session.error_flash = False

app.add_processor( web.loadhook( permission_loadhook ) )
app.add_processor( web.loadhook( flash_loadhook ) )
app.add_processor( web.loadhook( feeder_loadhook ) )
app.add_processor( web.unloadhook( flash_unloadhook ) )

####### Start the Feeder #######

feeder = Process( target=smf.feeder.run )
feeder.daemon = True
feeder.start()

####### Start the Server #######
try:
	app.run()
except Exception, e:
	feeder.terminate()
	feeder.join()