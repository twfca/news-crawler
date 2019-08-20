create table if not exists articles (
    id INTEGER primary key autoincrement,
    url TEXT unique,
    title TEXT,
    content TEXT,
    author_id INTEGER,
    trend_id INTEGER,
    website_id INTEGER,
    timestamp INTEGER
);
create table if not exists authors (
    id INTEGER primary key autoincrement,
    name TEXT unique
    website_id INTEGER
);
create table if not exists keywords (
    id INTEGER primary key autoincrement,
    name TEXT unique
);
create table if not exists trends (
    id INTEGER primary key autoincrement,
    keyword_id INTEGER,
    timestamp INTEGER,
    unique(keyword_id, timestamp)
);
create table if not exists websites (
    id INTEGER primary key autoincrement,
    name TEXT unique
    url TEXT unique
);