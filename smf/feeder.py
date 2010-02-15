# -*- coding: utf-8 -*-

import time
from datetime import datetime
import feedparser
import sqlite3
import ConfigParser
import util

def run ( config_path ):
	config = ConfigParser.RawConfigParser()
	config.read( config_path )
	conn = sqlite3.connect( config.get( 'Database', 'path' ) )
	cursor = conn.cursor()
	while True:
		try:
			res = cursor.execute( 'SELECT [id], [url], [modified], [etag], [interval] FROM [feeds] WHERE [checked] + [interval] < ?', ( util.timestamp(), ) )
			for row in res:
				try:
					d = feedparser.parse( row[1], etag=row[3], modified=row[2] )
					if not d.has_key( 'status' ):
						raise Exception( 'Error fetching content. Bad URL?' )
					if d.status != 200 and d.status != 301 and d.status != 302 and d.status != 304:
						raise Exception( d.debug_message)
					if not d.feed.has_key( 'title' ):
						raise Exception( "Content does not appear to be an RSS feed." )
				except Exception, e:
					conn.execute( "INSERT INTO [log] ( [logged], [type], [message] ) VALUES ( ?, ?, ? )", ( util.timestamp(), 'ERROR', 'Error fetching feed #' + str( row[0] ) + ": " + str( e ) ) )
					conn.execute( "UPDATE [feeds] SET [checked] = ? WHERE [id] = ?", ( util.timestamp() - int( row[4] / 2 ), row[0] ) )
					continue
				
				try:
					if d.status == 304:
						conn.execute( "UPDATE [feeds] SET [checked] = ? WHERE [id] = ?", ( util.timestamp(), row[0] ) )
					else:
						count = 0
						for entry in d.entries:
							result = conn.execute( "SELECT COUNT(*) FROM messages WHERE [feed_id] = ? AND [uuid] = ?", ( row[0], entry.id ) )
							if 0 != result[0][0]:
								break
							
							conn.execute( "INSERT INTO messages ( [feed_id], [fetched], [posted], [title], [link], [uuid], [content] ) VALUES ( ?, ?, ?, ?, ?, ?, ? )", ( row[0], util.timestamp(), util.timestamp( entry.date_parsed ), entry.title, entry.link, entry.id, entry.content) )

						if d.has_key( 'etag' ):
							etag = d.etag
						else:
							etag = ''
						
						if d.has_key( 'modified' ):
							modified = modified
						else:
							modified = datetime.now().timetuple()

						conn.execute( "UPDATE [feeds] SET [checked] = ?, [modified] = ?, [etag] = ? WHERE [id] = ?", ( util.timestamp(), modified, etag, row[0] ) )
						conn.execute( "INSERT INTO [log] ( [logged], [type], [message] ) VALUES ( ?, ?, ? )", ( util.timestamp(), 'UPDATE', 'Updated feed #' + str( row[0] ) + " with " + count + " new entries." ) )
				except Exception, e:
					conn.execute( "INSERT INTO [log] ( [logged], [type], [message] ) VALUES ( ?, ?, ? )", ( util.timestamp(), 'ERROR', 'Error parsing feed #' + str( row[0] ) + ": " + str( e ) ) )

			time.sleep( 30 ) # Arbitrary...
		except KeyboardInterrupt, e:
			return

# http://www.feedparser.org/docs/http-etag.html
#def fetch_feed ( url, etag, last_modified ):
	#d = feedparser.parse( url, etag=etag, modified=last_modified )
	#d.stats # 304 Not Changed
	#d.feed.title
	#d.feed.link
	#d.feed.description
	#d.entries
	#d.entries[0].title
	#d.entries[0].link
	#d.entries[0].description
	#d.entries[0].date_parsed
	#d.entries[0].id

def new_feed ( url ):
	try:
		d = feedparser.parse( url )
		if not d.has_key( 'status' ):
			raise Exception( 'Error fetching content. Bad URL?' )
		if d.status != 200 and d.status != 301 and d.status != 302:
			raise Exception( d.debug_message)
		if not d.feed.has_key( 'title' ):
			raise Exception( "Content does not appear to be an RSS feed." )
		
		if d.has_key( 'etag' ):
			etag = d.etag
		else:
			etag = ''
		
		if d.has_key( 'modified' ):
			modified = modified
		else:
			modified = datetime.now().timetuple()
		
		return { 'url': d.href, 'title': d.feed.title, 'link': d.feed.link, 'description': d.feed.description, 'etag': etag, 'modified': modified }
	except Exception, e:
		return str( e )