create table users (
    username varchar(255) primary key,
    password varchar(255) not null,
    type varchar(20) not null,
    id varchar(10) not null,
    rsl smallint not null,
    asl smallint not null,
    wsl smallint not null
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
    married bool not null,
    msl smallint not null,
    asl smallint not null,
    csl smallint not null
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
    married bool not null,
    msl smallint not null,
    asl smallint not null,
    csl smallint not null
);

create table patients (
    reception_id varchar(10) primary key,
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
    msl smallint not null,
    asl smallint not null,
    csl smallint not null
);

create table employees (
    personnel_id varchar(10) primary key,
    first_name varchar(255),
    last_name varchar(255),
    national_code varchar(10),
    role varchar(255) not null,
    section varchar(255) not null,
    employment_date date not null,
    age int not null,
    gender char not null,
    salary int not null,
    married bool not null,
    msl smallint not null,
    asl smallint not null,
    csl smallint not null
);

create table reports (
    id serial primary key,
    username varchar(255) not null references users(username) on delete cascade,
    report text,
    msl smallint not null,
    asl smallint not null,
    csl smallint not null
);

create table inspector_reports (
    id serial primary key,
    username varchar(255) not null references users(username) on delete cascade,
    report text,
    msl smallint not null,
    asl smallint not null,
    csl smallint not null
);

create table manager_reports (
    id serial primary key,
    username varchar(255) not null references users(username) on delete cascade,
    report text,
    msl smallint not null,
    asl smallint not null,
    csl smallint not null
);

insert into employees values ('0', 'Admin', 'Admini', '0', 'system_manager', 'hospital', '2019-12-19', 22, 'M', 20, false, 4, 4, 4);
insert into users values ('root', 'admin', 'employees', '0', 4, 4, 3);
