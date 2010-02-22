# -*- coding: utf-8 -*-

import feedparser

import database
import util
import story

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