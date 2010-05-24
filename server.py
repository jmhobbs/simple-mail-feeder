# -*- coding: utf-8 -*-
from datetime import datetime
import time
import ConfigParser

import web

from multiprocessing import Process

from smf import constants
from smf import util
import smf.feeder
from smf import models

# Set up web.py
web.config.debug = False

urls = (
	"/", "index",
	"/login", "login",
	"/logout", "logout",
	
	"/admin/feeder/start", "start_feeder",
	"/admin/feeder/stop", "stop_feeder",
	
	"/admin/feeds", "list_feeds",
	
	"/admin/log", "show_log",
	
	"/user/subscribe", "user_subscribe",
	"/user/unsubscribe/(.*)", "user_unsubscribe",
	"/user/subscriptions", "user_subscriptions"
)

app = web.application( urls, locals() )
session = web.session.Session( app, web.session.DiskStore('sessions'), initializer={ 'authenticated': False, 'user_id': 0, 'is_admin': False, 'flash': False, 'set_flash': False, 'error_flash': False, 'set_error_flash': False } )
render = web.template.render( 'views/', base='layout', globals={'session': session} )

class index:
	def GET ( self ):
		return render.index( models.Subscription.get_subscriptions_count_for_user( session.user_id ) )

class show_log:
	def GET ( self ):
		logs = models.Log.get_logs()
		for log in logs:
			log.logged = datetime.fromtimestamp( int( log.logged ) ).ctime()
		return render.show_log( logs )

####### Session Management #######

class login:
	def GET( self ):
		if session.authenticated:
			raise web.seeother( '/' )
		return render.login()

	def POST( self ):
		i = web.input()
		
		user = models.User.check_credentials( i.email, i.password )
		
		if False == user:
			session.error_flash = "Invalid Credentials"
			return render.login()
		
		session.authenticated = True
		session.user_id = user.id
		session.is_admin = user.is_admin
		session.set_flash = "Logged In"
		raise web.seeother( '/' )

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
			feeder = Process( target=smf.feeder.run, args=( constants.DEFAULT_CONFIG, ) )
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
		return render.list_feeds( models.Feed.get_all() )

####### Subscription Management #######

class user_subscribe:
	def POST ( self ):
		i = web.input()
		feed = models.Feed.get_from_url( i.url )
		if None == feed:
			feed = models.Feed.new_from_url( i.url )
			if str == type( feed ):
				session.set_error_flash = 'Error adding subscription: ' + feed
				raise web.seeother( '/user/subscriptions' )

		models.Subscription.subscribe( feed.id, session.user_id )
		session.set_flash = 'Subscribed to  "' + feed.title + '"'
		raise web.seeother( '/user/subscriptions' )

class user_unsubscribe:
	def GET ( self, feed_id ):
		db.query( "DELETE FROM subscriptions WHERE feed_id = $feed_id AND user_id = $user_id", vars={ 'feed_id': feed_id, 'user_id': session.user_id } )
		session.set_flash = 'Unsubscribed!'
		raise web.seeother( '/user/subscriptions' )

class user_subscriptions:
	def GET ( self ):
		return render.user_subscriptions(
			models.Subscription.get_subscriptions_count_for_user( session.user_id ),
			models.Subscription.get_subscribed_feeds_for_user( session.user_id )
		)

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

feeder = Process( target=smf.feeder.run, args=( constants.DEFAULT_CONFIG, ) )
feeder.daemon = True
feeder.start()

####### Start the Server #######
try:
	app.run()
except Exception, e:
	feeder.terminate()
	feeder.join()