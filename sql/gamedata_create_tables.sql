BEGIN TRANSACTION;
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
CREATE TABLE IF NOT EXISTS "face" (
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
CREATE TABLE IF NOT EXISTS "buildings" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
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
CREATE TABLE IF NOT EXISTS "danges_res_drop" (
	"dange_id"	INTEGER NOT NULL,
	"res_name"	TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS "danges_enemies" (
	"dange_id"	INTEGER NOT NULL,
	"enemy_id"	INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS "enchantments_armor" (
	"id"	INTEGER NOT NULL UNIQUE,
	"mirror_dmg"	INTEGER NOT NULL DEFAULT 0 CHECK("mirror_dmg" > -1 AND "mirror_dmg" < 100),
	"physical_damage_decr"	INTEGER NOT NULL DEFAULT 0 CHECK("physical_damage_decr" > -1 AND "physical_damage_decr" < 100),
	"magic_damage_decr"	INTEGER NOT NULL DEFAULT 0 CHECK("magic_damage_decr" > -1 AND "magic_damage_decr" < 100),
	"element_damage_decr"	INTEGER NOT NULL DEFAULT 0 CHECK("element_damage_decr" > -1 AND "element_damage_decr" < 100),
	"no_damage_chance"	INTEGER NOT NULL DEFAULT 0 CHECK("no_damage_chance" > -1 AND "no_damage_chance" < 100),
	"health_buff"	INTEGER NOT NULL DEFAULT 0,
	"name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "enchantments_weapon" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	"physical_dmg_incr"	INTEGER NOT NULL DEFAULT 0 CHECK("physical_dmg_incr" > -1 AND "physical_dmg_incr" < 100),
	"stun_chance"	INTEGER NOT NULL DEFAULT 0 CHECK("stun_chance" > -1 AND "stun_chance" < 100),
	"crit_chance"	INTEGER NOT NULL DEFAULT 0 CHECK("crit_chance" > -1 AND "crit_chance" < 100),
	"bleeding_chance"	INTEGER NOT NULL DEFAULT 0 CHECK("bleeding_chance" > -1 AND "bleeding_chance" < 100),
	"armor_ignore_chance"	INTEGER NOT NULL DEFAULT 0 CHECK("armor_ignore_chance" > -1 AND "armor_ignore_chance" < 100),
	"vampirism"	INTEGER NOT NULL DEFAULT 0 CHECK("vampirism" > -1 AND "vampirism" < 100),
	"element_dmg_incr"	INTEGER NOT NULL DEFAULT 0 CHECK("element_dmg_incr" > -1 AND "element_dmg_incr" < 100),
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "base_items" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	"type"	TEXT NOT NULL CHECK("type" = 'armor' OR "type" = 'weapon' OR "type" = 'hat'),
	"strength"	INTEGER NOT NULL DEFAULT 1,
	"rarity"	INTEGER NOT NULL CHECK("rarity" > -2 AND "rarity" < 6),
	"cost"	INTEGER NOT NULL DEFAULT 1,
	"filename"	TEXT NOT NULL,
	"class"	TEXT NOT NULL,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "enemies" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	"health"	INTEGER NOT NULL DEFAULT 1,
	"attack"	INTEGER NOT NULL DEFAULT 1,
	"defence"	INTEGER NOT NULL DEFAULT 1,
	"filename"	TEXT NOT NULL,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "danges" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT,
	"fights"	INTEGER NOT NULL DEFAULT 1 CHECK("fights" > 0),
	"filename"	INTEGER,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "res" (
	"id"	INTEGER NOT NULL UNIQUE,
	"Name"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "buffs" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	"stun"	INTEGER NOT NULL,
	"dmg"	INTEGER NOT NULL,
	"element"	TEXT NOT NULL,
	"time"	INTEGER NOT NULL,
	"defence"	INTEGER NOT NULL,
	"miss"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "consumable" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	"buff"	INTEGER NOT NULL,
	"dmg"	INTEGER NOT NULL,
	"area"	INTEGER NOT NULL,
	"target"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "craft_consumable" (
	"cons_id"	INTEGER NOT NULL,
	"res1_id"	INTEGER NOT NULL,
	"res2_id"	INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS "abilities" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	INTEGER NOT NULL,
	"class"	INTEGER NOT NULL,
	"buff"	INTEGER NOT NULL,
	"dmg_perc"	INTEGER NOT NULL,
	"element"	TEXT NOT NULL,
	"area"	INTEGER NOT NULL,
	"target"	TEXT NOT NULL,
	"tier"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "craft_items" (
	"id"	INTEGER NOT NULL UNIQUE,
	"item_tier"	INTEGER NOT NULL,
	"item_type"	INTEGER NOT NULL,
	"class"	INTEGER NOT NULL,
	"res1_id"	INTEGER NOT NULL,
	"res1_count"	INTEGER NOT NULL,
	"res2_id"	INTEGER NOT NULL,
	"res2_count"	INTEGER NOT NULL,
	"gold_count"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
COMMIT;
