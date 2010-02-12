CREATE TABLE [feeds] ([id] INTEGER PRIMARY KEY AUTOINCREMENT, [title] VARCHAR(255), [url] VARCHAR(255), [added] DATETIME, [fetched] DATETIME, [etag] VARCHAR(255), [interval] INTEGER);
CREATE TABLE [messages] ([id] INTEGER PRIMARY KEY AUTOINCREMENT, [feed_id] INTEGER REFERENCES [feeds](id), [fetched] DATETIME, [item_count] INTEGER, [content] TEXT);
CREATE TABLE [subscriptions] ([id] INTEGER PRIMARY KEY AUTOINCREMENT, [feed_id] INTEGER REFERENCES [feeds](id), [user_id] INTEGER REFERENCES [users](id));
CREATE TABLE [users] ([id] INTEGER PRIMARY KEY AUTOINCREMENT, [is_admin] BOOLEAN, [email] VARCHAR(255), [password] VARCHAR(255));