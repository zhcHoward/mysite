drop table if exists articles;
create table articles (
    id integer primary key autoincrement,
    title text not null,
    content text not null,
    time datetime default (datetime('now', '+8 hour'))
);

drop table if exists updates;
create table updates (
    id integer primary key autoincrement,
    updates text not null,
    time datetime default (datetime('now', '+8 hour'))
);