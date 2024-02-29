BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "servers" (
	"id"	INTEGER,
	"address"	TEXT NOT NULL,
	"username"	TEXT NOT NULL,
	"password"	TEXT NOT NULL,
	"timestamp"	REAL NOT NULL UNIQUE,
	"config_description"	TEXT NOT NULL,
	"commands"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO "servers" VALUES (1,'','','',1709046656.08189,'system message 1','command 1');
INSERT INTO "servers" VALUES (2,'','','',1709046657.08189,'system message 2','command 2');
INSERT INTO "servers" VALUES (3,'','','',1709046658.08189,'system message 3','command 3');
COMMIT;
