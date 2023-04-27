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
INSERT INTO "hair" ("id","name") VALUES (1,'Вариант 1'),
 (2,'Вариант 2'),
 (3,'Вариант 3'),
 (4,'Вариант 4'),
 (5,'Вариант 5');
INSERT INTO "shoulders" ("id","name") VALUES (1,'Вариант 1'),
 (2,'Вариант 2'),
 (3,'Вариант 3'),
 (4,'Вариант 4'),
 (5,'Вариант 5');
INSERT INTO "face" ("id","name") VALUES (1,'Вариант 1'),
 (2,'Вариант 2'),
 (3,'Вариант 3'),
 (4,'Вариант 4'),
 (5,'Вариант 5');
INSERT INTO "ranks" ("id","name","exp_to_earn") VALUES (1,'Новичок',0),
 (2,'Стажёр',500),
 (3,'Слабый воин',1000),
 (4,'Посредственный войн',2000),
 (5,'Узнаваемый солдат',4000),
 (6,'Кандидат в легионеры',8000),
 (7,'Джуниор-легионер',16000),
 (8,'Миддл-легионер',32000),
 (9,'Сеньор-легионер',64000),
 (10,'Гвардеец императора',128000);
INSERT INTO "buildings" ("id","name") VALUES (1,'Дом поручений'),
 (2,'Храм Хроноса'),
 (3,'Лаборатория'),
 (4,'Дом гильдий'),
 (5,'Кузница'),
 (6,'Арена');
INSERT INTO "tasks" ("id","name","description","difficulty","exp_reward","item_reward","type","is_multiplayer") VALUES (1,'Собрать дикорастущие травы','Соберите редкую траву из леса на юге, которая растет только утром и только на определенной поляне. Трава необходима для приготовления зелья лечения.',1,50,'Нет','small',0),
 (2,'Отыскать пропавшего купца','Найдите пропавшего купца в лесу на севере. Он заблудился и не может вернуться в город. Купец несет с собой драгоценные камни, которые нужно вернуть его заказчику в городе.',2,100,'Нет','medium',0),
 (3,'Покорить древнего дракона','Один из игроков должен покорить древнего дракона и забрать его чешую. Эта чешуя необходима для создания легендарного оружия для драконоборцев.',3,200,'armor','class_license',0),
 (4,'Обезвредить культистов','Группа игроков должна обезвредить культистов, которые пытаются открыть портал в мир демонов. Они находятся в тайной пещере на горе, их лагерь охраняется монстрами.',4,400,'Нет','special',1),
 (5,'Купить определенный вид цветка','Поговорить с торговцем на рынке и купить определенный вид редкого цветка для алхимического зелья.',1,50,'Нет','small',0),
 (6,'Найти спрятанный сундук','Найти спрятанный сундук в заброшенной шахте и вернуть его владельцу, получив небольшую денежную награду.',2,100,'Нет','small',0),
 (7,'Уничтожить гнездо гигантских пауков','Уничтожить гнездо гигантских пауков в лесу, пользуясь своими знаниями в боевых искусствах или заклинаниях.',3,150,'Нет','medium',0),
 (8,'Собрать ресурсы для кузнеца','Собрать определенное количество ресурсов для местного кузнеца, чтобы тот смог создать новый меч или доспех для героя.',1,50,'Нет','small',0),
 (9,'Сбор ресурсов','В этом задании игроки должны собирать ресурсы на протяжении определенного времени (например, 24 часа). Задание доступно для группы игроков и не может быть выполнено в одиночку.',0,100,'Нет','random',1);
INSERT INTO "danges_res_drop" ("dange_id","res_name") VALUES (1,'1'),
 (1,'2'),
 (1,'3'),
 (2,'4'),
 (2,'5'),
 (2,'6'),
 (3,'7'),
 (3,'8'),
 (3,'9'),
 (4,'10'),
 (4,'1'),
 (4,'7');
INSERT INTO "danges_enemies" ("dange_id","enemy_id") VALUES (1,1),
 (1,2),
 (1,6),
 (2,7),
 (2,8),
 (2,11),
 (3,3),
 (3,5),
 (3,11),
 (4,3),
 (4,6),
 (4,10);
INSERT INTO "enchantments_armor" ("id","mirror_dmg","physical_damage_decr","magic_damage_decr","element_damage_decr","no_damage_chance","health_buff","name") VALUES (1,15,0,0,0,0,0,'Зеркало'),
 (2,0,25,0,0,0,0,'Дворфийская сталь'),
 (3,0,0,25,0,0,0,'Эльфийская вышивка'),
 (4,0,0,0,25,0,0,'Отвод '),
 (5,0,0,0,0,10,0,'Двоичность '),
 (6,0,0,0,0,0,30,'Кровавый набор');
INSERT INTO "enchantments_weapon" ("id","name","physical_dmg_incr","stun_chance","crit_chance","bleeding_chance","armor_ignore_chance","vampirism","element_dmg_incr") VALUES (1,'Звездная заточка',25,0,0,0,0,0,0),
 (2,'Элемент ',0,0,0,0,0,0,30),
 (3,'Тяжелая рука',0,35,0,0,0,0,0),
 (4,'Легкая рука',0,0,15,0,0,0,0),
 (5,'Зубчатые лезвия',0,0,0,15,0,0,0),
 (6,'Пустотный удар',0,0,0,0,10,0,0),
 (7,'Графское проклятье',0,0,0,0,0,50,0);
INSERT INTO "base_items" ("id","name","type","strength","rarity","cost","filename","class") VALUES (1,'Легкая броня','armor',100,1,1200,'ArcherRare1','Лучник'),
 (2,'Круглый Щит и меч','weapon',50,1,1200,'RareSwordWeapon1','Рыцарь'),
 (3,'Ассиметричная легкая броня','armor',105,1,1350,'ArcherRare2','Лучник'),
 (4,'Легкая броня с укрепленным жилетом','armor',110,1,1650,'ArcherRare3','Лучник'),
 (5,'Легкая броня с накидкой','armor',115,1,1500,'ArcherRare4','Лучник'),
 (6,'Одежда охотника','armor',110,1,1200,'HunterRare1','Охотник'),
 (7,'Охотничая жилетка','armor',117,1,1350,'HunterRare2','Охотник'),
 (8,'Ассимитричная охотнячая одежда','armor',124,1,1500,'HunterRare3','Охотник'),
 (9,'Крутая броня охотника','armor',131,1,1650,'HunterRare4','Охотник'),
 (10,'Балахон мага','armor',90,1,1200,'MageRare1','Маг'),
 (11,'Балахон с жилеткой','armor',95,1,1350,'MageRare3','Маг'),
 (12,'Балахон с накидкой','armor',100,1,1500,'MageRare2','Маг'),
 (13,'Плащ мага','armor',110,1,1650,'MageRare4','Маг'),
 (14,'Кольчужная броня','armor',120,1,1200,'SwordRare1','Рыцарь'),
 (15,'Укрепленная кольчуга','armor',130,1,1350,'SwordRare2','Рыцарь'),
 (16,'Железные латы','armor',140,1,1500,'SwordRare3','Рыцарь'),
 (17,'Железный Панцирь','armor',150,1,1650,'SwordRare4','Рыцарь'),
 (19,'Крупный деревянный щит и меч','weapon',55,1,1300,'RareSwordWeapon2','Рыцарь'),
 (20,'Крутой деревянный щит и меч','weapon',60,1,1400,'RareSwordWeapon3','Рыцарь'),
 (21,'Простой лук','weapon',60,1,1200,'RareArcherWeapon1','Лучник'),
 (22,'Деревянный рекурсивный лук','weapon',67,1,1400,'RareArcherWeapon2','Лучник'),
 (23,'Деревянный длинный лук','weapon',74,1,1300,'RareArcherWeapon2','Лучник'),
 (24,'Простые ножи','weapon',70,1,1200,'RareHunterWeapon3','Охотник'),
 (25,'Простой длинный клинок','weapon',80,1,1300,'RareHunterWeapon2','Охотник'),
 (26,'Простой изогнутый клинок','weapon',90,1,1400,'RareHunterWeapon1','Охотник'),
 (27,'Простая волшебная палочка','weapon',45,1,1200,'RareMageWeapon1','Маг'),
 (28,'Простой прямой жезл','weapon',50,1,1300,'RareMageWeapon2','Маг'),
 (29,'Простой жезл','weapon',55,1,1400,'RareMageWeapon3','Маг'),
 (30,'Накидка и пончо','armor',190,2,2000,'T2Archer2','Лучник'),
 (31,'Легкая броня с кольчугой','armor',195,2,2150,'T2Archer1','Лучник'),
 (32,'Броня лучника','armor',200,2,2300,'T2Archer3','Лучник');
INSERT INTO "enemies" ("id","name","health","attack","defence","filename") VALUES (1,'Слизень',250,60,5,'Slime'),
 (2,'Нежить',350,75,10,'Zombie'),
 (3,'Гоблин',400,100,30,'Goblin'),
 (4,'Призрак',300,120,32,'Ghost'),
 (5,'Варг',450,150,10,'Warg'),
 (6,'Вампир',500,176,35,'Vampir'),
 (7,'Тэнгу',450,210,30,'Tengu'),
 (8,'Горгона',500,260,45,'Duza'),
 (9,'Оборотень',550,220,40,'Wolf'),
 (10,'Бандит',375,70,20,'Bandit'),
 (11,'Троль',600,300,50,'Troll');
INSERT INTO "danges" ("id","name","fights","filename") VALUES (1,'Пещеры',2,'Caves'),
 (2,'Горный Хребет',2,'Peak'),
 (3,'Цветочные поля',3,'FlowerPlains'),
 (4,'Лагерь',1,'Camp');
INSERT INTO "res" ("id","Name") VALUES (1,'Метал'),
 (2,'Грибы'),
 (3,'Камни'),
 (4,'Древесина'),
 (5,'Хладовик'),
 (6,'Перья'),
 (7,'Яркосвет'),
 (8,'Подорожник'),
 (9,'Святая вода'),
 (10,'Золото');
INSERT INTO "buffs" ("id","name","stun","dmg","element","time","defence","miss") VALUES (1,'Каменная броня',0,0,'0',2,20,0),
 (2,'Первородная благодетель',0,-15,'0',2,0,0),
 (3,'Шок',1,0,'electric',1,0,0),
 (4,'Проницатель',0,0,'0',2,0,75),
 (5,'Обращен в мрамор',1,0,'0',2,1000000,0),
 (6,'Святой холод',1,-20,'water',1,1000000,0),
 (7,'Поднятые щиты',0,0,'0',3,15,0),
 (8,'Оглушен',1,0,'0',1,0,0),
 (9,'Защита',0,0,'0',3,7,0),
 (10,'Кровотечение',0,-30,'0',2,0,0),
 (11,'Восстановление',0,-10,'0',2,0,0),
 (12,'Божья помощь',0,0,'0',3,10,0),
 (13,'Южные ветра',0,0,'0',2,0,95),
 (14,'Металлическая кожа',0,0,'0',1,25,0),
 (15,'Ледянная душа',0,0,'0',2,-5,0),
 (16,'Грибное смещение',0,-5,'0',2,5,0),
 (17,'Ослепительное проклятие',0,-15,'0',3,0,0);
INSERT INTO "consumable" ("id","name","buff","dmg","area","target") VALUES (1,'Граната',0,15,1,'enemy'),
 (2,'Микстура Ивлева',0,-20,0,'friend'),
 (3,'Регенеративный эликсир',11,0,0,'friend'),
 (4,'Божественный эликсир',12,0,0,'friend'),
 (5,'Ветряное зелье',13,0,0,'friend'),
 (6,'Огненная банка',0,25,0,'enemy'),
 (7,'Зелье металлической кожи',14,0,0,'friend'),
 (8,'Склянка ледяной души',15,0,1,'enemy'),
 (9,'Микстура грибного смещения',16,0,1,'friend'),
 (10,'Жидкость ослепительного проклятия',17,10,1,'all');
INSERT INTO "craft_consumable" ("cons_id","res1_id","res2_id") VALUES (1,3,3),
 (2,8,7),
 (3,8,9),
 (4,9,7),
 (5,6,2),
 (6,10,1),
 (7,1,8),
 (8,5,4),
 (9,2,9),
 (10,6,7);
INSERT INTO "abilities" ("id","name","class","buff","dmg_perc","element","area","target","tier") VALUES (1,'Каменная броня','Маг',1,0,'0',0,'friend',1),
 (2,'Первородная благодетель','Маг',2,0,'0',0,'friend',1),
 (3,'Плотная кожа','Маг',0,-33,'0',1,'friend',1),
 (4,'Проводник','Маг',3,10,'electric',0,'enemy',1),
 (5,'Проницатель','Маг',4,0,'0',1,'friend',1),
 (6,'Мраморное касание','Маг',5,0,'0',0,'all',2),
 (7,'Морозная свежесть','Маг',6,-50,'water',0,'friend',2),
 (8,'Поднять Щиты','Рыцарь',7,0,'0',0,'self',1),
 (9,'Головная боль','Рыцарь',8,150,'0',0,'enemy',1),
 (10,'Взов защиты','Рыцарь',9,0,'0',1,'friend',1),
 (11,'Оглушающая стрела','Лучник',8,70,'0',0,'enemy',1),
 (12,'Обстрел','Лучник',0,75,'0',1,'enemy',1),
 (13,'Ахилесова пята','Лучник',10,200,'0',0,'enemy',1),
 (14,'Пронзающий удар','Охотник',10,250,'0',0,'enemy',1),
 (15,'Бросок клинка','Охотник',10,200,'0',0,'enemy',1),
 (16,'Омнислэш','Охотник',0,120,'0',1,'enemy',1);
INSERT INTO "craft_items" ("id","item_tier","item_type","class","res1_id","res1_count","res2_id","res2_count","gold_count") VALUES (1,1,'armor','sword',4,3,1,5,100),
 (2,1,'weapon','sword',1,5,7,4,120),
 (3,1,'armor','mage',7,3,8,5,100),
 (4,1,'weapon','mage',9,5,4,4,120),
 (5,1,'armor','archer',6,3,2,5,100),
 (6,1,'weapon','archer',2,5,3,4,120),
 (7,1,'armor','hunter',1,3,5,5,100),
 (8,1,'weapon','hunter',10,5,5,4,120),
 (9,2,'armor','sword',1,7,5,10,250),
 (10,2,'weapon','sword',10,11,5,9,280),
 (11,2,'armor','mage',4,7,1,10,250),
 (12,2,'weapon','mage',1,11,7,9,280),
 (13,2,'armor','archer',7,7,8,10,250),
 (14,2,'weapon','archer',9,11,4,9,280),
 (15,2,'armor','hunter',6,7,2,10,250),
 (16,2,'weapon','hunter',2,11,3,9,280),
 (17,3,'armor','sword',6,20,2,25,400),
 (18,3,'weapon','sword',2,30,3,24,450),
 (19,3,'armor','mage',1,20,5,25,400),
 (20,3,'weapon','mage',10,30,5,24,450),
 (21,3,'armor','archer',4,20,1,25,400),
 (22,3,'weapon','archer',1,30,7,24,450),
 (23,3,'armor','hunter',7,20,8,25,400),
 (24,3,'weapon','hunter',9,30,4,24,450),
 (25,4,'armor','sword',7,25,8,32,600),
 (26,4,'weapon','sword',9,37,4,31,650),
 (27,4,'armor','mage',6,25,2,32,600),
 (28,4,'weapon','mage',2,37,3,31,650),
 (29,4,'armor','archer',1,25,5,32,600),
 (30,4,'weapon','archer',10,37,5,31,650),
 (31,4,'armor','hunter',4,25,1,32,600),
 (32,4,'weapon','hunter',1,37,7,31,650);
COMMIT;
