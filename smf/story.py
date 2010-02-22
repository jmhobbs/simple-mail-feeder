# -*- coding: utf-8 -*-

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