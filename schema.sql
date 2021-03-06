CREATE TABLE IF NOT EXISTS [feeds] (
	[id] INTEGER PRIMARY KEY AUTOINCREMENT,
	[title] VARCHAR(255),
	[url] VARCHAR(255),
	[description] TEXT,
	[link] VARCHAR(255),
	[added] VARCHAR(12),
	[checked] VARCHAR(12),
	[modified] VARCHAR(255),
	[etag] VARCHAR(255),
	[interval] INTEGER
);

CREATE TABLE IF NOT EXISTS [stories] (
	[id] INTEGER PRIMARY KEY AUTOINCREMENT,
	[feed_id] INTEGER REFERENCES [feeds](id),
	[fetched] VARCHAR(12),
	[posted] VARCHAR(12),
	[uuid] VARCHAR(255),
	[title] VARCHAR(255),
	[link] VARCHAR(255),
	[content] TEXT
);

CREATE TABLE IF NOT EXISTS [users] (
	[id] INTEGER PRIMARY KEY AUTOINCREMENT,
	[is_admin] BOOLEAN,
	[email] VARCHAR(255),
	[password] VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS [subscriptions] (
	[id] INTEGER PRIMARY KEY AUTOINCREMENT,
	[feed_id] INTEGER REFERENCES [feeds](id),
	[user_id] INTEGER REFERENCES [users](id),
	[subscribed] VARCHAR(12)
);

CREATE TABLE IF NOT EXISTS [log] (
	[id] INTEGER PRIMARY KEY AUTOINCREMENT,
	[logged] VARCHAR(12),
	[level] VARCHAR(255),
	[message] TEXT
);