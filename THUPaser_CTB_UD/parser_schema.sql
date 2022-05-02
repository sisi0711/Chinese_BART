drop table if exists thuparser;
create table thuparser(
	id integer primary key autoincrement,
	sentence text not null,
	ip text,
	query_time text
);