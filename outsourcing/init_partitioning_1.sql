create table users (
    username varchar(255) primary key,
    password varchar(255) not null,
    type varchar(20) not null,
    hmac varchar(50) not null
);

create table physicians (
    personnel_id varchar(10) primary key,
    first_name varchar(255) not null,
    last_name varchar(255) not null,
    national_code varchar(10) not null unique,
    hmac varchar(50) not null
);

create table nurses (
    personnel_id varchar(10) primary key,
    first_name varchar(255),
    last_name varchar(255),
    national_code varchar(10) not null unique,
    hmac varchar(50) not null
);

create table patients (
    reception_id varchar(10) primary key,
    first_name varchar(255) not null,
    last_name varchar(255) not null,
    national_code varchar(10) not null unique,
    hmac varchar(50) not null
);

create table employees (
    personnel_id varchar(10) primary key,
    first_name varchar(255),
    last_name varchar(255),
    national_code varchar(10) not null unique,
    hmac varchar(50) not null
);

create table reports (
    id serial primary key,
    username varchar(255) not null references users(username) on delete cascade,
    hmac varchar(50) not null
);

create table inspector_reports (
    id serial primary key,
    username varchar(255) not null references users(username) on delete cascade,
    hmac varchar(50) not null
);

create table manager_reports (
    id serial primary key,
    username varchar(255) not null references users(username) on delete cascade,
    hmac varchar(50) not null
);

insert into employees values ('0', 'Admin', 'Admini', '0', 'XVHqVvsCTa0J6FihEsBoWdhnS2sTwVs/8HGLPINYoAM=');
insert into users values ('root', 'admin', 'employees', 'lgmMvtVknhuD88NhdHgWMb3odIdiJajEZPErlsiB04o=');
