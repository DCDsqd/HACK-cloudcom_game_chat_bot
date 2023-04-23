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
CREATE TABLE IF NOT EXISTS "skill" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	INTEGER NOT NULL,
	"class"	INTEGER NOT NULL,
	"buff"	INTEGER NOT NULL,
	"dmg_prec"	INTEGER NOT NULL,
	"element"	TEXT NOT NULL,
	"area"	INTEGER NOT NULL,
	"target"	TEXT NOT NULL,
	"tier"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "buff" (
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
INSERT INTO "hair" ("id","name") VALUES (1,'Вариант 1');
INSERT INTO "hair" ("id","name") VALUES (2,'Вариант 2');
INSERT INTO "hair" ("id","name") VALUES (3,'Вариант 3');
INSERT INTO "hair" ("id","name") VALUES (4,'Вариант 4');
INSERT INTO "hair" ("id","name") VALUES (5,'Вариант 5');
INSERT INTO "shoulders" ("id","name") VALUES (1,'Вариант 1');
INSERT INTO "shoulders" ("id","name") VALUES (2,'Вариант 2');
INSERT INTO "shoulders" ("id","name") VALUES (3,'Вариант 3');
INSERT INTO "shoulders" ("id","name") VALUES (4,'Вариант 4');
INSERT INTO "shoulders" ("id","name") VALUES (5,'Вариант 5');
INSERT INTO "face" ("id","name") VALUES (1,'Вариант 1');
INSERT INTO "face" ("id","name") VALUES (2,'Вариант 2');
INSERT INTO "face" ("id","name") VALUES (3,'Вариант 3');
INSERT INTO "face" ("id","name") VALUES (4,'Вариант 4');
INSERT INTO "face" ("id","name") VALUES (5,'Вариант 5');
INSERT INTO "ranks" ("id","name","exp_to_earn") VALUES (1,'Новичок',0);
INSERT INTO "ranks" ("id","name","exp_to_earn") VALUES (2,'Стажёр',500);
INSERT INTO "ranks" ("id","name","exp_to_earn") VALUES (3,'Слабый воин',1000);
INSERT INTO "ranks" ("id","name","exp_to_earn") VALUES (4,'Посредственный войн',2000);
INSERT INTO "ranks" ("id","name","exp_to_earn") VALUES (5,'Узнаваемый солдат',4000);
INSERT INTO "ranks" ("id","name","exp_to_earn") VALUES (6,'Кандидат в легионеры',8000);
INSERT INTO "ranks" ("id","name","exp_to_earn") VALUES (7,'Джуниор-легионер',16000);
INSERT INTO "ranks" ("id","name","exp_to_earn") VALUES (8,'Миддл-легионер',32000);
INSERT INTO "ranks" ("id","name","exp_to_earn") VALUES (9,'Сеньор-легионер',64000);
INSERT INTO "ranks" ("id","name","exp_to_earn") VALUES (10,'Гвардеец императора',128000);
INSERT INTO "buildings" ("id","name") VALUES (1,'Дом поручений');
INSERT INTO "buildings" ("id","name") VALUES (2,'Храм Хроноса');
INSERT INTO "buildings" ("id","name") VALUES (3,'Лаборатория');
INSERT INTO "buildings" ("id","name") VALUES (4,'Дом гильдий');
INSERT INTO "buildings" ("id","name") VALUES (5,'Кузница');
INSERT INTO "buildings" ("id","name") VALUES (6,'Рынок');
INSERT INTO "buildings" ("id","name") VALUES (7,'Арена');
INSERT INTO "buildings" ("id","name") VALUES (8,'Великая библиотека');
INSERT INTO "buildings" ("id","name") VALUES (9,'Зал легионеров');
INSERT INTO "tasks" ("id","name","description","difficulty","exp_reward","item_reward","type","is_multiplayer") VALUES (1,'Собрать дикорастущие травы','Соберите редкую траву из леса на юге, которая растет только утром и только на определенной поляне. Трава необходима для приготовления зелья лечения.',1,50,'Нет','small',0);
INSERT INTO "tasks" ("id","name","description","difficulty","exp_reward","item_reward","type","is_multiplayer") VALUES (2,'Отыскать пропавшего купца','Найдите пропавшего купца в лесу на севере. Он заблудился и не может вернуться в город. Купец несет с собой драгоценные камни, которые нужно вернуть его заказчику в городе.',2,100,'Нет','medium',0);
INSERT INTO "tasks" ("id","name","description","difficulty","exp_reward","item_reward","type","is_multiplayer") VALUES (3,'Покорить древнего дракона','Один из игроков должен покорить древнего дракона и забрать его чешую. Эта чешуя необходима для создания легендарного оружия для драконоборцев.',3,200,'armor','class_license',0);
INSERT INTO "tasks" ("id","name","description","difficulty","exp_reward","item_reward","type","is_multiplayer") VALUES (4,'Обезвредить культистов','Группа игроков должна обезвредить культистов, которые пытаются открыть портал в мир демонов. Они находятся в тайной пещере на горе, их лагерь охраняется монстрами.',4,400,'Нет','special',1);
INSERT INTO "tasks" ("id","name","description","difficulty","exp_reward","item_reward","type","is_multiplayer") VALUES (5,'Купить определенный вид цветка','Поговорить с торговцем на рынке и купить определенный вид редкого цветка для алхимического зелья.',1,50,'Нет','small',0);
INSERT INTO "tasks" ("id","name","description","difficulty","exp_reward","item_reward","type","is_multiplayer") VALUES (6,'Найти спрятанный сундук','Найти спрятанный сундук в заброшенной шахте и вернуть его владельцу, получив небольшую денежную награду.',2,100,'Нет','small',0);
INSERT INTO "tasks" ("id","name","description","difficulty","exp_reward","item_reward","type","is_multiplayer") VALUES (7,'Уничтожить гнездо гигантских пауков','Уничтожить гнездо гигантских пауков в лесу, пользуясь своими знаниями в боевых искусствах или заклинаниях.',3,150,'Нет','medium',0);
INSERT INTO "tasks" ("id","name","description","difficulty","exp_reward","item_reward","type","is_multiplayer") VALUES (8,'Собрать ресурсы для кузнеца','Собрать определенное количество ресурсов для местного кузнеца, чтобы тот смог создать новый меч или доспех для героя.',1,50,'Нет','small',0);
INSERT INTO "tasks" ("id","name","description","difficulty","exp_reward","item_reward","type","is_multiplayer") VALUES (9,'Сбор ресурсов','В этом задании игроки должны собирать ресурсы на протяжении определенного времени (например, 24 часа). Задание доступно для группы игроков и не может быть выполнено в одиночку.',0,100,'Нет','random',1);
INSERT INTO "danges_res_drop" ("dange_id","res_name") VALUES (1,'1');
INSERT INTO "danges_res_drop" ("dange_id","res_name") VALUES (1,'2');
INSERT INTO "danges_res_drop" ("dange_id","res_name") VALUES (1,'3');
INSERT INTO "danges_res_drop" ("dange_id","res_name") VALUES (2,'4');
INSERT INTO "danges_res_drop" ("dange_id","res_name") VALUES (2,'5');
INSERT INTO "danges_res_drop" ("dange_id","res_name") VALUES (2,'6');
INSERT INTO "danges_res_drop" ("dange_id","res_name") VALUES (3,'7');
INSERT INTO "danges_res_drop" ("dange_id","res_name") VALUES (3,'8');
INSERT INTO "danges_res_drop" ("dange_id","res_name") VALUES (3,'9');
INSERT INTO "danges_res_drop" ("dange_id","res_name") VALUES (4,'10');
INSERT INTO "danges_res_drop" ("dange_id","res_name") VALUES (4,'1');
INSERT INTO "danges_res_drop" ("dange_id","res_name") VALUES (4,'7');
INSERT INTO "danges_enemies" ("dange_id","enemy_id") VALUES (1,1);
INSERT INTO "danges_enemies" ("dange_id","enemy_id") VALUES (1,2);
INSERT INTO "danges_enemies" ("dange_id","enemy_id") VALUES (1,6);
INSERT INTO "danges_enemies" ("dange_id","enemy_id") VALUES (2,7);
INSERT INTO "danges_enemies" ("dange_id","enemy_id") VALUES (2,8);
INSERT INTO "danges_enemies" ("dange_id","enemy_id") VALUES (2,11);
INSERT INTO "danges_enemies" ("dange_id","enemy_id") VALUES (3,3);
INSERT INTO "danges_enemies" ("dange_id","enemy_id") VALUES (3,5);
INSERT INTO "danges_enemies" ("dange_id","enemy_id") VALUES (3,11);
INSERT INTO "danges_enemies" ("dange_id","enemy_id") VALUES (4,3);
INSERT INTO "danges_enemies" ("dange_id","enemy_id") VALUES (4,6);
INSERT INTO "danges_enemies" ("dange_id","enemy_id") VALUES (4,10);
INSERT INTO "enchantments_armor" ("id","mirror_dmg","physical_damage_decr","magic_damage_decr","element_damage_decr","no_damage_chance","health_buff","name") VALUES (1,15,0,0,0,0,0,'Зеркало');
INSERT INTO "enchantments_armor" ("id","mirror_dmg","physical_damage_decr","magic_damage_decr","element_damage_decr","no_damage_chance","health_buff","name") VALUES (2,0,25,0,0,0,0,'Дворфийская сталь');
INSERT INTO "enchantments_armor" ("id","mirror_dmg","physical_damage_decr","magic_damage_decr","element_damage_decr","no_damage_chance","health_buff","name") VALUES (3,0,0,25,0,0,0,'Эльфийская вышивка');
INSERT INTO "enchantments_armor" ("id","mirror_dmg","physical_damage_decr","magic_damage_decr","element_damage_decr","no_damage_chance","health_buff","name") VALUES (4,0,0,0,25,0,0,'Отвод ');
INSERT INTO "enchantments_armor" ("id","mirror_dmg","physical_damage_decr","magic_damage_decr","element_damage_decr","no_damage_chance","health_buff","name") VALUES (5,0,0,0,0,10,0,'Двоичность ');
INSERT INTO "enchantments_armor" ("id","mirror_dmg","physical_damage_decr","magic_damage_decr","element_damage_decr","no_damage_chance","health_buff","name") VALUES (6,0,0,0,0,0,30,'Кровавый набор');
INSERT INTO "enchantments_weapon" ("id","name","physical_dmg_incr","stun_chance","crit_chance","bleeding_chance","armor_ignore_chance","vampirism","element_dmg_incr") VALUES (1,'Звездная заточка',25,0,0,0,0,0,0);
INSERT INTO "enchantments_weapon" ("id","name","physical_dmg_incr","stun_chance","crit_chance","bleeding_chance","armor_ignore_chance","vampirism","element_dmg_incr") VALUES (2,'Элемент ',0,0,0,0,0,0,30);
INSERT INTO "enchantments_weapon" ("id","name","physical_dmg_incr","stun_chance","crit_chance","bleeding_chance","armor_ignore_chance","vampirism","element_dmg_incr") VALUES (3,'Тяжелая рука',0,35,0,0,0,0,0);
INSERT INTO "enchantments_weapon" ("id","name","physical_dmg_incr","stun_chance","crit_chance","bleeding_chance","armor_ignore_chance","vampirism","element_dmg_incr") VALUES (4,'Легкая рука',0,0,15,0,0,0,0);
INSERT INTO "enchantments_weapon" ("id","name","physical_dmg_incr","stun_chance","crit_chance","bleeding_chance","armor_ignore_chance","vampirism","element_dmg_incr") VALUES (5,'Зубчатые лезвия',0,0,0,15,0,0,0);
INSERT INTO "enchantments_weapon" ("id","name","physical_dmg_incr","stun_chance","crit_chance","bleeding_chance","armor_ignore_chance","vampirism","element_dmg_incr") VALUES (6,'Пустотный удар',0,0,0,0,10,0,0);
INSERT INTO "enchantments_weapon" ("id","name","physical_dmg_incr","stun_chance","crit_chance","bleeding_chance","armor_ignore_chance","vampirism","element_dmg_incr") VALUES (7,'Графское проклятье',0,0,0,0,0,50,0);
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (1,'Легкая броня','armor',50,1,1200,'ArcherRare1','archer');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (2,'Круглый Щит и меч','weapon',20,1,1200,'RareSwordWeapon1','archer');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (3,'Ассиметричная легкая броня','armor',55,1,1350,'ArcherRare2','archer');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (4,'Легкая броня с укрепленным жилетом','armor',65,1,1650,'ArcherRare3','archer');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (5,'Легкая броня с накидкой','armor',60,1,1500,'ArcherRare4','archer');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (7,'Легкая повязка','hat',20,1,800,'ArcherRareHat1','archer');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (8,'Легкая бандана','hat',25,1,900,'ArcherRareHat2','archer');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (9,'Забавная шляпа меткости','hat',30,1,1000,'ArcherRareHat3','archer');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (10,'Обод меткости','hat',35,1,1100,'ArcherRareHat4','archer');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (11,'Одежда охотника','armor',55,1,1200,'HunterRare1','hunter');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (12,'Охотничая жилетка','armor',65,1,1350,'HunterRare2','hunter');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (13,'Ассимитричная охотнячая одежда','armor',75,1,1500,'HunterRare3','hunter');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (14,'Крутая броня охотника','armor',85,1,1650,'HunterRare4','hunter');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (15,'Бандана охотника','hat',25,1,800,'HunterRareHat1','hunter');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (16,'Капюшон охотника','hat',32,1,900,'HunterRareHat3','hunter');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (17,'Крутая охотничая бандана','hat',39,1,1000,'HunterRareHat2','hunter');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (18,'Маска охотника','hat',46,1,1100,'HunterRareHat4','hunter');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (19,'Балахон мага','armor',45,1,1200,'MageRare1','mage');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (20,'Балахон с жилеткой','armor',50,1,1350,'MageRare3','mage');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (21,'Балахон с накидкой','armor',55,1,1500,'MageRare2','mage');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (22,'Плащ мага','armor',60,1,1650,'MageRare4','mage');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (23,'Шляпа колдуна','hat',18,1,800,'MageRareHat1','mage');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (24,'Шапка мага','hat',22,1,900,'MageRareHat2','mage');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (25,'Капюшон мага','hat',26,1,1000,'MageRareHat3','mage');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (26,'Цилиндр мага','hat',30,1,1100,'MageRareHat4','mage');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (27,'Кольчужная броня','armor',60,1,1200,'SwordRare1','sword');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (28,'Укрепленная кольчуга','armor',67,1,1350,'SwordRare2','sword');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (29,'Железные латы','armor',74,1,1500,'SwordRare3','sword');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (30,'Железный Панцирь','armor',81,1,1650,'SwordRare4','sword');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (31,'Железная шапка','hat',25,1,800,'SwordRareHat1','sword');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (32,'Железный цилиндр','hat',35,1,900,'SwordRareHat2','sword');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (33,'Железная широкая шляпа','hat',45,1,1000,'SwordRareHat4','sword');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (34,'Железный шлем','hat',55,1,1100,'SwordRareHat3','sword');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (35,'Крупный деревянный щит и меч','weapon',25,1,1300,'RareSwordWeapon2','sword');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (36,'Крутой деревянный щит и меч','weapon',30,1,1400,'RareSwordWeapon3','sword');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (37,'Простой лук','weapon',25,1,1200,'RareArcherWeapon1','archer');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (38,'Деревянный рекурсивный лук','weapon',39,1,1400,'RareArcherWeapon2','archer');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (39,'Деревянный длинный лук','weapon',32,1,1300,'RareArcherWeapon2','archer');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (40,'Простые ножи','weapon',30,1,1200,'RareHunterWeapon3','hunter');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (41,'Простой длинный клинок','weapon',37,1,1300,'RareHunterWeapon2','hunter');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (42,'Простой изогнутый клинок','weapon',44,1,1400,'RareHunterWeapon1','hunter');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (43,'Простая волшебная палочка','weapon',20,1,1200,'RareMageWeapon1','mage');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (44,'Простой прямой жезл','weapon',25,1,1300,'RareMageWeapon2','mage');
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (45,'Простой жезл','weapon',30,1,1400,'RareMageWeapon3','mage');
INSERT INTO "enemies" ("id","name","health","attack","defence","filename") VALUES (1,'Слизень',250,60,5,'Slime');
INSERT INTO "enemies" ("id","name","health","attack","defence","filename") VALUES (2,'Нежить',350,75,10,'Zombie');
INSERT INTO "enemies" ("id","name","health","attack","defence","filename") VALUES (3,'Гоблин',400,100,30,'Goblin');
INSERT INTO "enemies" ("id","name","health","attack","defence","filename") VALUES (4,'Призрак',300,120,32,'Ghost');
INSERT INTO "enemies" ("id","name","health","attack","defence","filename") VALUES (5,'Варг',450,150,10,'Warg');
INSERT INTO "enemies" ("id","name","health","attack","defence","filename") VALUES (6,'Вампир',500,176,35,'Vampir');
INSERT INTO "enemies" ("id","name","health","attack","defence","filename") VALUES (7,'Тэнгу',450,210,30,'Tengu');
INSERT INTO "enemies" ("id","name","health","attack","defence","filename") VALUES (8,'Горгона',500,260,45,'Duza');
INSERT INTO "enemies" ("id","name","health","attack","defence","filename") VALUES (9,'Оборотень',550,220,40,'Wolf');
INSERT INTO "enemies" ("id","name","health","attack","defence","filename") VALUES (10,'Бандит',375,70,20,'Bandit');
INSERT INTO "enemies" ("id","name","health","attack","defence","filename") VALUES (11,'Троль',600,300,50,'Troll');
INSERT INTO "danges" ("id","name","fights","filename") VALUES (1,'Пещеры',2,'Caves');
INSERT INTO "danges" ("id","name","fights","filename") VALUES (2,'Горный Хребет',2,'Peak');
INSERT INTO "danges" ("id","name","fights","filename") VALUES (3,'Цветочные поля',3,'FlowerPlains');
INSERT INTO "danges" ("id","name","fights","filename") VALUES (4,'Лагерь',1,'Camp');
INSERT INTO "res" ("id","Name") VALUES (1,'Метал');
INSERT INTO "res" ("id","Name") VALUES (2,'Грибы');
INSERT INTO "res" ("id","Name") VALUES (3,'Камни');
INSERT INTO "res" ("id","Name") VALUES (4,'Древесина');
INSERT INTO "res" ("id","Name") VALUES (5,'Хладовик');
INSERT INTO "res" ("id","Name") VALUES (6,'Перья');
INSERT INTO "res" ("id","Name") VALUES (7,'Яркосвет');
INSERT INTO "res" ("id","Name") VALUES (8,'Подорожник');
INSERT INTO "res" ("id","Name") VALUES (9,'Святая вода');
INSERT INTO "res" ("id","Name") VALUES (10,'Золото');
INSERT INTO "skill" ("id","name","class","buff","dmg_prec","element","area","target","tier") VALUES (1,'Каменная броня','mage',1,0,'0',0,'friend',1);
INSERT INTO "skill" ("id","name","class","buff","dmg_prec","element","area","target","tier") VALUES (2,'Первородная благодетель','mage',2,0,'0',0,'friend',1);
INSERT INTO "skill" ("id","name","class","buff","dmg_prec","element","area","target","tier") VALUES (3,'Плотная кожа','mage',0,-33,'0',1,'friend',1);
INSERT INTO "skill" ("id","name","class","buff","dmg_prec","element","area","target","tier") VALUES (4,'Проводник ','mage',3,10,'electric',0,'enemy',1);
INSERT INTO "skill" ("id","name","class","buff","dmg_prec","element","area","target","tier") VALUES (5,'Проницатель ','mage',4,0,'0',1,'friend',1);
INSERT INTO "skill" ("id","name","class","buff","dmg_prec","element","area","target","tier") VALUES (6,'Мраморное касание','mage',5,0,'0',0,'all',2);
INSERT INTO "skill" ("id","name","class","buff","dmg_prec","element","area","target","tier") VALUES (7,'Морозная свежесть','mage',6,-50,'water',0,'friend',2);
INSERT INTO "skill" ("id","name","class","buff","dmg_prec","element","area","target","tier") VALUES (8,'Поднять Щиты','sword',7,0,'0',0,'self',1);
INSERT INTO "skill" ("id","name","class","buff","dmg_prec","element","area","target","tier") VALUES (9,'Головная боль','sword',8,150,'0',0,'enemy',1);
INSERT INTO "skill" ("id","name","class","buff","dmg_prec","element","area","target","tier") VALUES (10,'Взов защиты','sword',9,0,'0',1,'friend',1);
INSERT INTO "skill" ("id","name","class","buff","dmg_prec","element","area","target","tier") VALUES (11,'Оглушающая стрела','archer',8,70,'0',0,'enemy',1);
INSERT INTO "skill" ("id","name","class","buff","dmg_prec","element","area","target","tier") VALUES (12,'Обстрел','archer',0,75,'0',1,'enemy',1);
INSERT INTO "skill" ("id","name","class","buff","dmg_prec","element","area","target","tier") VALUES (13,'Ахилесова пята','archer',10,200,'0',0,'enemy',1);
INSERT INTO "skill" ("id","name","class","buff","dmg_prec","element","area","target","tier") VALUES (14,'Пронзающий удар','hunter',10,250,'0',0,'enemy',1);
INSERT INTO "skill" ("id","name","class","buff","dmg_prec","element","area","target","tier") VALUES (15,' Бросок клинка','hunter',10,200,'0',0,'enemy',1);
INSERT INTO "skill" ("id","name","class","buff","dmg_prec","element","area","target","tier") VALUES (16,'Омнислэш','hunter',0,120,'0',1,'enemy',1);
INSERT INTO "buff" ("id","name","stun","dmg","element","time","defence","miss") VALUES (1,'Каменная броня',0,0,'0',2,20,0);
INSERT INTO "buff" ("id","name","stun","dmg","element","time","defence","miss") VALUES (2,'Первородная благодетель',0,-15,'0',2,0,0);
INSERT INTO "buff" ("id","name","stun","dmg","element","time","defence","miss") VALUES (3,'Шок',1,0,'electric',1,0,0);
INSERT INTO "buff" ("id","name","stun","dmg","element","time","defence","miss") VALUES (4,'Проницатель ',0,0,'0',0,0,75);
INSERT INTO "buff" ("id","name","stun","dmg","element","time","defence","miss") VALUES (5,'Обращен в мрамор',1,0,'0',2,1000000,0);
INSERT INTO "buff" ("id","name","stun","dmg","element","time","defence","miss") VALUES (6,'Святой холод',1,-20,'water',1,1000000,0);
INSERT INTO "buff" ("id","name","stun","dmg","element","time","defence","miss") VALUES (7,'Поднятые щиты',0,0,'0',3,15,0);
INSERT INTO "buff" ("id","name","stun","dmg","element","time","defence","miss") VALUES (8,'Оглушен',1,0,'0',1,0,0);
INSERT INTO "buff" ("id","name","stun","dmg","element","time","defence","miss") VALUES (9,'Защита',0,0,'0',3,7,0);
INSERT INTO "buff" ("id","name","stun","dmg","element","time","defence","miss") VALUES (10,'Кровотечение',0,-30,'0',2,0,0);
COMMIT;
