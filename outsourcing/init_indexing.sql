create table users (
    id serial primary key,
    tuple text not null,
    username_i smallint not null,
    password_i smallint not null,
    type_i smallint not null,
    id_i smallint not null,
    rsl_i smallint not null,
    asl_i smallint not null,
    wsl_i smallint not null,
    hmac varchar(50) not null
);

create table physicians (
    id serial primary key,
    tuple text not null,
    personnel_id_i smallint not null,
    national_code_i smallint not null,
    management_role_i smallint not null,
    section_i smallint not null,
    age_i smallint not null,
    gender_i smallint not null,
    salary_i smallint not null,
    married_i smallint not null,
    msl_i smallint not null,
    asl_i smallint not null,
    csl_i smallint not null,
    hmac varchar(50) not null
);

create table nurses (
    id serial primary key,
    tuple text not null,
    personnel_id_i smallint not null,
    national_code_i smallint not null,
    section_i smallint not null,
    age_i smallint not null,
    gender_i smallint not null,
    salary_i smallint not null,
    married_i smallint not null,
    msl_i smallint not null,
    asl_i smallint not null,
    csl_i smallint not null,
    hmac varchar(50) not null
);

create table patients (
    id serial primary key,
    tuple text not null,
    reception_id_i smallint not null,
    national_code_i smallint not null,
    age_i smallint not null,
    gender_i smallint not null,
    section_i smallint not null,
    physician_i smallint not null,
    nurse_i smallint not null,
    msl_i smallint not null,
    asl_i smallint not null,
    csl_i smallint not null,
    hmac varchar(50) not null
);

create table employees (
    id serial primary key,
    tuple text not null,
    personnel_id_i smallint not null,
    national_code_i smallint not null,
    role_i smallint not null,
    section_i smallint not null,
    age_i smallint not null,
    gender_i smallint not null,
    salary_i smallint not null,
    married_i smallint not null,
    msl_i smallint not null,
    asl_i smallint not null,
    csl_i smallint not null,
    hmac varchar(50) not null
);

create table reports (
    id serial primary key,
    tuple text not null,
    username_i smallint not null,
    msl_i smallint not null,
    asl_i smallint not null,
    csl_i smallint not null,
    hmac varchar(50) not null
);

create table inspector_reports (
    id serial primary key,
    tuple text not null,
    username_i smallint not null,
    msl_i smallint not null,
    asl_i smallint not null,
    csl_i smallint not null,
    hmac varchar(50) not null
);

create table manager_reports (
    id serial primary key,
    tuple text not null,
    username_i smallint not null,
    msl_i smallint not null,
    asl_i smallint not null,
    csl_i smallint not null,
    hmac varchar(50) not null
);

insert into employees (tuple, personnel_id_i, national_code_i, role_i, section_i, age_i, gender_i, salary_i, married_i, msl_i, asl_i, csl_i, hmac) values ('lNoB/Qz7sUwkmf3dXi5vVvNdTj+YQYOyQPsIj1H4IqMkBljPuJ9tMug6E7Vw8/+KHdrAEW95l/cNfjSRDMdTwLS8d6UYUBncI13xxqFwAYFPXqSguOOw77Qjcn0B6EylqxECdpwhDix7ejhFPwab8/tycTrQz/bG5wjA0FBzgkww3Q==', 14, 77, 77, 44, 189, 0, 145, 7, 4, 4, 4, 'iuwOJxF26UwQXXIIfVJ7yudZRV+hS3hN+hRS4ACjsmA=');
insert into users (tuple, username_i, password_i, type_i, id_i, rsl_i, asl_i, wsl_i, hmac) values ('0jZKCFjduGMgnToqhC9Z2iKBnxX2eTOwPykMKjfaIcr1yAglHdaeHv+0F+FMSMBA1tw2DAne1frL8nETzceFGxKktUgGyEeL0u07Hw==', 94, 5, 197, 189, 4, 4, 3, 'OR9+lmAiGoe0qXq8/8QAmODZRSIC7pzdGaUMM49WvOc=');
