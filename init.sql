create table users (
    username varchar(255) primary key,
    password varchar(255) not null,
    type varchar(20) not null
);

create table physicians (
    personnel_id varchar(10) primary key,
    first_name varchar(255) not null,
    last_name varchar(255) not null,
    national_code varchar(10) not null unique,
    proficiency varchar(255) not null,
    management_role varchar(255) not null,
    section varchar(255) not null,
    employment_date date not null,
    age int not null,
    gender char not null,
    salary int not null,
    marital_status char not null,
    username varchar(255) not null references users(username) ON DELETE CASCADE,
    s_asl smallint not null default 3,
    s_rsl smallint not null default 3,
    s_wsl smallint not null default 3,
    o_asl smallint not null default 3,
    o_msl smallint not null default 4,
    o_csl smallint not null default 3
);

create table nurses (
    personnel_id varchar(10) primary key,
    first_name varchar(255),
    last_name varchar(255),
    national_code varchar(10),
    section varchar(255) not null,
    employment_date date not null,
    age int not null,
    gender char not null,
    salary int not null,
    marital_status char not null,
    username varchar(255) not null references users(username) ON DELETE CASCADE,
    s_asl smallint not null default 2,
    s_rsl smallint not null default 2,
    s_wsl smallint not null default 2,
    o_asl smallint not null default 3,
    o_msl smallint not null default 4,
    o_csl smallint not null default 3
);

create table patients (
    reception_id serial primary key,
    first_name varchar(255) not null,
    last_name varchar(255) not null,
    national_code varchar(10) not null,
    age int not null,
    gender char not null,
    sickness_type varchar(255) not null,
    section varchar(255) not null,
    physician varchar(10) not null references physicians(personnel_id) on delete cascade,
    nurse varchar(255) not null references nurses(personnel_id) on delete cascade,
    drugs text,
    username varchar(255) not null references users(username) ON DELETE CASCADE,
    s_asl smallint not null default 1,
    s_rsl smallint not null default 1,
    s_wsl smallint not null default 1,
    o_asl smallint not null default 3,
    o_msl smallint not null default 4,
    o_csl smallint not null default 3
);

create table employees (
    personnel_id varchar(10) primary key,
    first_name varchar(255),
    last_name varchar(255),
    national_code varchar(10),
    role varchar(255) not null,
    employment_date date not null,
    age int not null,
    gender char not null,
    salary int not null,
    marital_status char not null,
    username varchar(255) not null references users(username) ON DELETE CASCADE,
    s_asl smallint not null default 3,
    s_rsl smallint not null default 4,
    s_wsl smallint not null default 3,
    o_asl smallint not null default 3,
    o_msl smallint not null default 4,
    o_csl smallint not null default 3
);

create table reports (
    id serial primary key,
    username varchar(255) not null references users(username) on delete cascade,
    report text,
    o_asl smallint not null,
    o_msl smallint not null,
    o_csl smallint not null
);

create table inspector_reports (
    id serial primary key,
    username varchar(255) not null references users(username) on delete cascade,
    report text,
    o_asl smallint not null,
    o_msl smallint not null,
    o_csl smallint not null
);

create table manager_reports (
    id serial primary key,
    username varchar(255) not null references users(username) on delete cascade,
    report text,
    report_id int unique references reports(id) on delete cascade,
    o_asl smallint not null,
    o_msl smallint not null,
    o_csl smallint not null
);
