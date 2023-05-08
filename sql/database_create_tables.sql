BEGIN TRANSACTION;
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
CREATE TABLE IF NOT EXISTS "friends" (
	"sender_id"	INTEGER NOT NULL,
	"receiver_id"	INTEGER NOT NULL,
	"is_accepted"	INTEGER NOT NULL DEFAULT 0,
	"date_accepted"	TEXT
);
CREATE TABLE IF NOT EXISTS "local_events" (
	"id"	INTEGER UNIQUE,
	"type"	TEXT NOT NULL,
	"start_time"	TEXT NOT NULL,
	"result"	TEXT NOT NULL DEFAULT "in progress",
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "local_events_participants" (
	"id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS "user_daily_tasks" (
	"user_id"	INTEGER NOT NULL,
	"task_id"	INTEGER NOT NULL,
	"is_completed"	INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS "user_daily_tasks_updated" (
	"user_id"	INTEGER NOT NULL UNIQUE,
	"last_update"	TEXT NOT NULL,
	PRIMARY KEY("user_id")
);
CREATE TABLE IF NOT EXISTS "chats" (
	"id"	INTEGER NOT NULL,
	"chat_id"	INTEGER NOT NULL,
	"title"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "duels" (
	"id"	INTEGER NOT NULL UNIQUE,
	"sender_id"	INTEGER NOT NULL,
	"receiver_id"	INTEGER,
	"status"	TEXT,
	"outcome"	INTEGER DEFAULT 0 CHECK("outcome" > -1 AND "outcome" < 3),
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "items_owned" (
	"meta_item_id"	INTEGER NOT NULL UNIQUE,
	"owner_id"	INTEGER NOT NULL,
	"base_item_id"	INTEGER NOT NULL,
	"enchantments"	TEXT,
	"elements"	TEXT,
	"date"	TEXT NOT NULL,
	PRIMARY KEY("meta_item_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "global_events_participants" (
	"id"	INTEGER,
	"user_id"	INTEGER
);
CREATE TABLE IF NOT EXISTS "global_events" (
	"id"	INTEGER UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	"descr"	TEXT NOT NULL CHECK(length("descr") < 1000),
	"start_time"	TEXT NOT NULL,
	"duration"	INTEGER NOT NULL DEFAULT 5,
	"exp_reward"	INTEGER DEFAULT 0,
	"is_complited"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "user_multiplayer_daily_tasks" (
	"user_id"	INTEGER,
	"task_id"	INTEGER,
	"is_completed"	INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS "multiplayer_task_participants" (
	"id"	INTEGER NOT NULL UNIQUE,
	"task_id"	INTEGER,
	"user1_id"	INTEGER,
	"user2_id"	INTEGER NOT NULL DEFAULT 0,
	"user3_id"	INTEGER NOT NULL DEFAULT 0,
	"user4_id"	INTEGER NOT NULL DEFAULT 0,
	"is_user2_accepted"	INTEGER NOT NULL DEFAULT 0,
	"is_user3_accepted"	INTEGER NOT NULL DEFAULT 0,
	"is_user4_accepted"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "res_owned" (
	"user_id"	INTEGER NOT NULL,
	"res_id"	INTEGER NOT NULL,
	"count"	INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS "consumable_owned" (
	"user_id"	INTEGER NOT NULL,
	"consum_id"	INTEGER NOT NULL,
	"count"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("user_id","consum_id")
);
CREATE TABLE IF NOT EXISTS "guild_house" (
	"id"	INTEGER NOT NULL UNIQUE,
	"sender_id"	INTEGER,
	"res_id"	INTEGER,
	"count"	INTEGER,
	"is_got"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "users" (
	"id"	INTEGER UNIQUE,
	"username"	TEXT NOT NULL,
	"personal_username"	TEXT,
	"game_class"	TEXT,
	"game_subclass"	TEXT NOT NULL DEFAULT 'None',
	"exp"	INTEGER NOT NULL DEFAULT 0,
	"hair_id"	INTEGER NOT NULL DEFAULT 1,
	"face_id"	TEXT NOT NULL DEFAULT 1,
	"shoulders_id"	INTEGER NOT NULL DEFAULT 1,
	"admin"	INTEGER NOT NULL DEFAULT 0,
	"active_armor_meta_id"	INTEGER DEFAULT 1,
	"active_weapon_meta_id"	INTEGER DEFAULT 2,
	"money"	INTEGER NOT NULL DEFAULT 0,
	"fatum"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("id" AUTOINCREMENT)
);
COMMIT;
