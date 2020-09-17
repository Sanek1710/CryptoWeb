DROP TABLE if exists file_db;

CREATE TABLE file_db (
	_uid bigint,
	_name varchar(260),
	_type char,
	_path varchar(260),
	PRIMARY KEY (_uid, _name, _path)
);