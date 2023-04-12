CREATE TABLE IF NOT EXISTS "users" (
	"id"	INTEGER UNIQUE,
	"username"	TEXT NOT NULL UNIQUE,
	"personal_username"	TEXT UNIQUE,
	"game_class"	TEXT,
	"game_subclass"	TEXT NOT NULL DEFAULT 'None',
	"exp"	INTEGER NOT NULL DEFAULT 0,
	"hair_id"	INTEGER NOT NULL DEFAULT 1,
	"face_id"	TEXT NOT NULL DEFAULT 1,
	"shoulders_id"	INTEGER NOT NULL DEFAULT 1,
	"admin"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "global_events" (
	"id"	INTEGER UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	"descr"	TEXT NOT NULL CHECK(length("descr") < 1000),
	"start_time"	TEXT NOT NULL,
	"duration"	INTEGER NOT NULL DEFAULT 5,
	"participants"	TEXT,
	"exp_reward"	INTEGER DEFAULT 0,
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

CREATE TABLE IF NOT EXISTS "polls" (
	"poll_id"	INTEGER UNIQUE,
	"for"	INTEGER NOT NULL DEFAULT 0,
	"against"	INTEGER NOT NULL DEFAULT 0,
	"is_ended"	INTEGER NOT NULL DEFAULT 0,
	"name"	TEXT,
	"descr"	TEXT CHECK(length("descr") < 1000),
	"start_time"	TEXT,
	"duration"	INTEGER NOT NULL DEFAULT 5,
	"exp_reward"	INTEGER DEFAULT 0,
	PRIMARY KEY("poll_id")
);

CREATE TABLE IF NOT EXISTS "items_owned" (
	"owner"	INTEGER NOT NULL,
	"item"	INTEGER NOT NULL,
	"date"	TEXT NOT NULL,
	PRIMARY KEY("owner")
);

CREATE TABLE IF NOT EXISTS "friends" (
	"sender_id"	INTEGER NOT NULL,
	"receiver_id"	INTEGER NOT NULL,
	"is_accepted"	INTEGER NOT NULL DEFAULT 0,
	"date_accepted"	TEXT,
	PRIMARY KEY("sender_id")
);

CREATE TABLE IF NOT EXISTS "user_daily_tasks" (
	"user_id"	INTEGER NOT NULL,
	"task_id"	INTEGER NOT NULL,
	PRIMARY KEY("user_id")
);

CREATE TABLE IF NOT EXISTS "user_daily_tasks_updated" (
	"user_id"	INTEGER NOT NULL,
	"last_update"	TEXT NOT NULL,
	PRIMARY KEY("user_id")
);

CREATE TABLE IF NOT EXISTS "global_events_participants" (
	"id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS "local_events_participants" (
	"id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS "duels" (
	"id"	INTEGER NOT NULL UNIQUE,
	"sender_id"	INTEGER NOT NULL,
	"receiver_id"	INTEGER,
	"status"	TEXT
);

CREATE TABLE IF NOT EXISTS "chats" (
	"id"	INTEGER NOT NULL,
	"chat_id"	INTEGER NOT NULL,
	"title"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
