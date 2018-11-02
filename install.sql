-- Drop table

-- DROP TABLE public.budget

CREATE TABLE public.budget (
	category varchar NULL,
	title varchar NULL,
	"month" varchar NULL,
	budget1 numeric(10,2) NULL,
	budget2 numeric(10,2) NULL,
	budget3 numeric(10,2) NULL,
	fixed bool NULL,
	ignore_title bool NULL
)
WITH (
	OIDS=TRUE
);

-- Drop table

-- DROP TABLE public.patterns

CREATE TABLE public.patterns (
	pattern varchar NOT NULL,
	category varchar NOT NULL,
	title varchar NULL,
	maxamount numeric(10,2) NULL,
	fixed bool NOT NULL
)
WITH (
	OIDS=TRUE
);

-- Drop table

-- DROP TABLE public.transactions

CREATE TABLE public.transactions (
	"date" date NOT NULL,
	description varchar NOT NULL,
	amount numeric(10,2) NOT NULL,
	balance numeric(10,2) NOT NULL,
	"type" varchar NULL,
	category varchar NULL,
	title varchar NULL,
	fixed bool NULL,
	CONSTRAINT transactions_pk PRIMARY KEY (date, description, amount, balance)
)
WITH (
	OIDS=TRUE
);
