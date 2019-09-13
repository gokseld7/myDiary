CREATE TABLE UsersDiary(
    id SERIAL PRIMARY KEY,
    username varchar(255),
    password varchar(500),
    email varchar(255),
    key
);

CREATE TABLE Articles(
    id SERIAL PRIMARY KEY,
    author varchar(255),
    name text,
    content text,
    last_edited varchar(255)
);