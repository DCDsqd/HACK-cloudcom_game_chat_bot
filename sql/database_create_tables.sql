CREATE TABLE IF NOT EXISTS "users" (
	"id"	INTEGER UNIQUE,
	"username"	TEXT NOT NULL UNIQUE,
	"personal_username"	TEXT UNIQUE,
	"game_class"	TEXT,
	"exp"	INTEGER NOT NULL DEFAULT 0,
	"hair_id"	INTEGER NOT NULL DEFAULT 1,
	"face_id"	INTEGER NOT NULL DEFAULT 1,
	"shoulders_id"	INTEGER NOT NULL DEFAULT 1,
	PRIMARY KEY("id" AUTOINCREMENT)
)

CREATE TABLE IF NOT EXISTS "global_events" (
	"id"	INTEGER UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	"descr"	TEXT NOT NULL CHECK(length("descr") < 1000),
	"start_time"	TEXT NOT NULL,
	"duration"	INTEGER NOT NULL DEFAULT 5,
	"participants"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "local_events" (
	"id"	INTEGER UNIQUE,
	"type"	TEXT NOT NULL,
	"start_time"	TEXT NOT NULL,
	"participants"	TEXT NOT NULL,
	"result"	TEXT NOT NULL DEFAULT "in progress",
	PRIMARY KEY("id" AUTOINCREMENT)
);
