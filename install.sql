BEGIN TRANSACTION;
DROP TABLE IF EXISTS `transactions`;
CREATE TABLE IF NOT EXISTS `transactions` (
	`date`	TEXT NOT NULL,
	`description`	TEXT NOT NULL,
	`amount`	NUMERIC NOT NULL,
	`balance`	NUMERIC NOT NULL,
	`type`	TEXT DEFAULT 1,
	`category`	TEXT,
	`title`	TEXT,
	`fixed`	INTEGER
);
DROP TABLE IF EXISTS `patterns`;
CREATE TABLE IF NOT EXISTS `patterns` (
	`pattern`	TEXT ( 2000000000 ) NOT NULL,
	`category`	TEXT ( 2000000000 ) NOT NULL,
	`title`	text,
	`maxamount`	NUMERIC ( 2000000000 , 10 ),
	`fixed`	INTEGER NOT NULL DEFAULT 0
);
DROP TABLE IF EXISTS `month_budget`;
CREATE TABLE IF NOT EXISTS `month_budget` (
	`category`	TEXT,
	`title`	TEXT,
	`month`	TEXT,
	`budget1`	NUMERIC,
	`budget2`	NUMERIC,
	`budget3`	NUMERIC,
	`fixed`	INTEGER,
	PRIMARY KEY(`category`,`title`,`month`)
);
DROP TABLE IF EXISTS `budget`;
CREATE TABLE IF NOT EXISTS `budget` (
	`category`	TEXT,
	`title`	TEXT,
	`budget1`	NUMERIC,
	`budget2`	NUMERIC,
	`budget3`	NUMERIC,
	PRIMARY KEY(`category`,`title`)
);
DROP INDEX IF EXISTS `transactions_date_IX`;
CREATE INDEX IF NOT EXISTS `transactions_date_IX` ON `transactions` (
	`date`	DESC
);
DROP INDEX IF EXISTS `transactions_UQ`;
CREATE UNIQUE INDEX IF NOT EXISTS `transactions_UQ` ON `transactions` (
	`date`	DESC,
	`amount`,
	`balance`
);
COMMIT;
