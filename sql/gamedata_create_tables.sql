CREATE TABLE IF NOT EXISTS "face" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "hair" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "shoulders" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "ranks" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	"exp_to_earn"	INTEGER UNIQUE,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "tasks" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	"description"	TEXT NOT NULL UNIQUE,
	"difficulty"	INTEGER NOT NULL,
	"exp_reward"	INTEGER NOT NULL,
	"item_reward"	TEXT NOT NULL DEFAULT 'Нет',
	"type"	TEXT NOT NULL,
	"is_multiplayer"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "danges" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT,
	"fights"	INTEGER NOT NULL DEFAULT 1 CHECK(fights > 0),
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "danges_enemies" (
	"dange_id"	INTEGER NOT NULL,
	"enemy_id"	INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS "danges_res_drop" (
	"dange_id"	INTEGER NOT NULL,
	"res_name"	TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS "enemies" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	"health"	INTEGER NOT NULL DEFAULT 1,
	"attack"	INTEGER NOT NULL DEFAULT 1,
	"defence"	INTEGER NOT NULL DEFAULT 1,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "base_items" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	"type"	TEXT NOT NULL CHECK("type" = 'armor' OR "type" = 'weapon'),
	"strength"	INTEGER NOT NULL DEFAULT 1,
	"rarity"	INTEGER NOT NULL CHECK("rarity" > -2 AND "rarity" < 6),
	"cost"	INTEGER NOT NULL DEFAULT 1,
	PRIMARY KEY("id")
);