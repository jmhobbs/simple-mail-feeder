# -*- coding: utf-8 -*-
CREATE TABLE IF NOT EXISTS [users] ([id] INTEGER PRIMARY KEY AUTOINCREMENT, [is_admin] BOOLEAN, [email] VARCHAR(255), [password] VARCHAR(255));