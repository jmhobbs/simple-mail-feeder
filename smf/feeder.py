# -*- coding: utf-8 -*-

import time
import feedparser
import sqlite3
import ConfigParser

def run ():
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
		if d.status != 200 and d.status != 301 and d.status != 302:
			raise Exception( d.debug_message)
		if not d.feed.has_key( 'title' ):
			raise Exception( "Content does not appear to be an RSS feed." )
		return { 'url': d.href, 'title': d.feed.title, 'link': d.feed.link, 'description': d.feed.description, 'etag': d.etag, 'modified': d.modified }
	except Exception, e:
		return str( e )