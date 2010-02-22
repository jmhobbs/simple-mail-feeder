# -*- coding: utf-8 -*-
CREATE TABLE IF NOT EXISTS [subscriptions] ([id] INTEGER PRIMARY KEY AUTOINCREMENT, [feed_id] INTEGER REFERENCES [feeds](id), [user_id] INTEGER REFERENCES [users](id));