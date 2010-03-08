# -*- coding: utf-8 -*-

# db.query( "SELECT COUNT(*) AS subscriptions FROM subscriptions WHERE user_id=$user_id", vars={ 'user_id': session.user_id } )
# db.select( 'users', { 'email': i.email }, where="email = $email", limit=1 )

import web

import bcrypt
import feedparser
import util

db = web.database( dbn='sqlite', db='smf.db3' )

################################################################################

class User:
	
	id = None
	is_admin = False
	email = ''
	password = ''
	
	@staticmethod
	def check_credentials ( email, password ):
		res = db.select( 'users', { 'email': email }, where="[email] = $email", limit=1 )
		try:
			if bcrypt.hashpw( password, res[0].password ) == res[0].password:
				return res[0].id
			else:
				return False
		except Exception, e:
			Log.log( 'Problem during user log in: %s' % e )
			return False

################################################################################

class Subscription:
	
	id = None
	feed_id = None
	user_id = None
	subscribed = 0
	
	def __init__ ( self, row=None ):
		if None != row:
			self.id = row[0]
			self.feed_id = row[1]
			self.user_id = row[2]
			self.subscribed = row[3]
	
	@staticmethod
	def subscribe ( feed_id, user_id ):
		db.query( "INSERT INTO [subscriptions] ( [feed_id], [user_id], [subscribed] ) VALUES ( $feed_id, $user_id, $subscribed )", vars={ 'feed_id': feed_id, 'user_id': user_id, 'subscribed': util.timestamp() } )

	@staticmethod
	def unsubscribe ( feed_id, user_id ):
		db.query( "DELETE FROM [subscriptions] WHERE [feed_id] = $feed_id AND [user_id] = $user_id", vars={ 'feed_id': feed_id, 'user_id': user_id } )
	
	@staticmethod
	def get_subscriptions_by_feed ( feed_id ):
		return db.select( 'subscriptions', { 'feed_id': feed_id }, where="[feed_id] = $feed_id" )

	@staticmethod
	def get_subscriptions_by_user ( user_id ):
		return db.select( 'subscriptions', { 'user_id': user_id }, where="[user_id] = $user_id" )

################################################################################

class Story:
	
	id = None
	feed_id = None
	fetched = ''
	posted = ''
	uuid = ''
	title = ''
	link = ''
	content = ''

	def __init__ ( self, row=None ):
		if row != None:
			self.id = row[0]
			self.feed_id = row[1]
			self.fetched = row[2]
			self.posted = row[3]
			self.uuid = row[4]
			self.title = row[5]
			self.link = row[6]
			self.content = row[7]
		return
	
	def create ( self ):
		"""
		Save a new story to the database.
		"""
		database.cursor.execute( "INSERT INTO [stories] ( [feed_id], [fetched], [posted], [uuid], [title], [link], [content] ) VALUES ( ?, ?, ?, ?, ?, ?, ? )", ( self.feed_id, self.fetched, self.posted, self.uuid, self.title, self.link, self.content ) )
		database.connection.commit()
	
	@staticmethod
	def exists ( feed_id, uuid ):
		"""
		Check if a story exists in the database.
		"""
		result = cursor.execute( "SELECT COUNT(*) FROM stories WHERE [feed_id] = ? AND [uuid] = ?", ( feed_id, uuid ) )
		return 0 != result[0][0]

################################################################################

class Feed:
	
	id = None
	title = ''
	url = ''
	description = ''
	link = ''
	added = ''
	checked = ''
	modified = ''
	interval = 900

	def __init__ ( self, row=None ):
		if row != None:
			self.id = row[0]
			self.title = row[1]
			self.url = row[2]
			self.description = row[3]
			self.link = row[4]
			self.added = row[5]
			self.checked = row[6]
			self.modified = int( row[7] )
			self.etag = row[8]
			self.interval = row[9]
		return
	
	def fetch ( self ):
		try:
			fp = feedparser.parse( self.url, etag=self.etag, modified=self.modified )
			if not fp.has_key( 'status' ):
				raise Exception( 'Error fetching content. Bad URL?' )
			if fp.status != 200 and fp.status != 301 and fp.status != 302 and fp.status != 304:
				raise Exception( d.debug_message)
			if not sp.feed.has_key( 'title' ):
				raise Exception( "Content does not appear to be an RSS feed." )
		except Exception, e:
			database.log( 'Error fetching feed #%d: %s' % ( self.id, e ) )
			self.mark_missed()
		else:
			try:
				if d.status == 304:
					self.mark_checked()
				else:
					count = 0
					for entry in d.entries:
						# Quit when we find one we already have
						if story.Story.exists( self.id, entry.id ):
							break
						
						new_story = story.Story()
						new_story.feed_id = self.id
						new_story.fetched = util.timestamp()
						new_story.posted = util.timestamp( entry.date_parsed )
						new_story.uuid = entry.id
						new_story.title = entry.title
						new_story.link = entry.link
						new_story.content = entry.content # TODO: Only keep a snippet?
						new_story.create()

					if fp.has_key( 'etag' ):
						self.etag = fp.etag
					else:
						self.etag = ''
					
					if fp.has_key( 'modified' ):
						self.modified = fp.modified
					else:
						self.modified = datetime.now().timetuple()

					self.mark_updated()
					database.log( "Updated feed #%d with %d new entries." % ( self.id, count ), database.LOG_DEBUG )
			except Exception, e:
				database.log( "Error parsing feed #%d: %s" % ( self.id, e ) )

	def mark_checked ( self ):
		database.cursor.execute( "UPDATE [feeds] SET [checked] = ? WHERE [id] = ?", ( util.timestamp() , self.id ) )
		database.connection.commit()
	
	def mark_missed ( self ):
		database.cursor.execute( "UPDATE [feeds] SET [checked] = ? WHERE [id] = ?", ( util.timestamp() - int( self.interval / 2 ), self.id ) )
		database.connection.commit()

	def mark_updated ( self ):
		database.cursor.execute( "UPDATE [feeds] SET [checked] = ?, [modified] = ?, [etag] = ? WHERE [id] = ?", ( util.timestamp(), self.modified, self.etag, self.id ) )
		database.connection.commit()

	#def create ( self ):
		#database.cursor.execute

	@staticmethod
	def find ( id ):
		res = database.cursor.execute( "SELECT * FROM feeds WHERE id = ? LIMIT 0,1", ( id, ) )
		row = res.fetchone()
		if None == row:
			return None
		else:
			return Feed( row )
	
	@staticmethod
	def find_expired ():
		res = database.cursor.execute( "SELECT * FROM [feeds] WHERE [checked] + [interval] < ?", ( util.timestamp(), ) )
		feeds = []
		for row in res:
			feeds.append( Feed( row ) )
		return feeds
		
################################################################################


class Log:

	LOG_DEBUG='DEBUG'
	LOG_WARNING='WARNING'
	LOG_ERROR='ERROR'
	LOG_FATAL='FATAL'

	@staticmethod
	def log ( message, level='ERROR' ):
		db.insert( 'log', logged=util.timestamp(), level=level, message=message )

	#@staticmethod
	#def get_logs ( self, count=20, page=0, levels=('ERROR', 'FATAL') ):
		## TODO: Should be something like "is_iterable" right?
		#if tuple == type( levels ) or list == type( levels ) or dict == type( levels ):
			#type_string = 'WHERE ('
			#for level in levels:
				#type_string = type_string + ' [level] == ? OR'
				
			#if 0 != len( levels ):
				#type_string = type_string[:-2] + ")"
			#else:
				#type_string = ' '
		#else:
			#type_string = ' '
			#levels = []

		#type_string = "%s LIMIT %d,%d" % ( type_string, ( count * page ), count )
		
		#result = self.cursor.execute( "SELECT * FROM [log] " + type_string , levels )
		
		#logs = []
		#for log in result:
			#logs.append( log )

		#return logs