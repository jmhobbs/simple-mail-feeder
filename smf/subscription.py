# -*- coding: utf-8 -*-

import database

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
		database.cursor.execute( "INSERT INTO [subscriptions] ( [feed_id], [user_id], [subscribed] ) VALUES ( ?, ?, ? )", ( feed_id, user_id, util.timestamp() ) );
		database.connection.commit()

	@staticmethod
	def unsubscribe ( feed_id, user_id ):
		database.cursor.execute( "DELETE FROM [subscriptions] WHERE [feed_id] = ? AND [user_id] = ?", ( feed_id, user_id ) );
		database.connection.commit()
	
	@staticmethod
	def get_subscriptions_by_feed ( feed_id ):
		return databse.cursor.execute( "SELECT * FROM [subscriptions] WHERE [feed_id] = ?", ( feed_id, ) ).fetchAll()

	@staticmethod
	def get_subscriptions_by_user ( user_id ):
		return databse.cursor.execute( "SELECT * FROM [subscriptions] WHERE [user_id] = ?", ( user_id, ) ).fetchAll()