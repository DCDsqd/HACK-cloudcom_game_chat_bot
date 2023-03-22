CREATE TABLE IF NOT EXISTS "events" (
	"id"	INTEGER UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	"descr"	TEXT,
	"start_time"	TEXT NOT NULL,
	"duration"	INTEGER NOT NULL,
	"participants"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "users" (
	"id"	INTEGER,
	"username"	TEXT NOT NULL,
	"personal_username"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);