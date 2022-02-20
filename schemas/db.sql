-- SQL code to create schema for tapas

-- Dumping structure for table public.jobs
CREATE TABLE IF NOT EXISTS "jobs" (
	"job_id" VARCHAR NOT NULL DEFAULT '',
	"id" INTEGER NOT NULL DEFAULT 'nextval(''jobs_id_seq''::regclass)',
	"status" VARCHAR NULL DEFAULT NULL
);


-- Dumping structure for table public.results
CREATE TABLE IF NOT EXISTS "results" (
	"slug" VARCHAR NOT NULL,
	"id" INTEGER NOT NULL DEFAULT 'nextval(''results_id_seq''::regclass)',
	"file1" VARCHAR NULL DEFAULT NULL,
	"file2" VARCHAR NULL DEFAULT NULL,
	"text1" VARCHAR NULL DEFAULT NULL,
	"text2" VARCHAR NULL DEFAULT NULL,
	"score" DOUBLE PRECISION(53) NULL DEFAULT NULL
);
