create table users (
    id serial primary key,
    tuple text not null,
    username_i smallint not null,
    password_i smallint not null,
    type_i smallint not null,
    id_i smallint not null,
    rsl_i smallint not null,
    asl_i smallint not null,
    wsl_i smallint not null
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
    csl_i smallint not null
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
    csl_i smallint not null
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
    csl_i smallint not null
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
    csl_i smallint not null
);

create table reports (
    id serial primary key,
    tuple text not null,
    username_i smallint not null,
    msl_i smallint not null,
    asl_i smallint not null,
    csl_i smallint not null
);

create table inspector_reports (
    id serial primary key,
    tuple text not null,
    username_i smallint not null,
    msl_i smallint not null,
    asl_i smallint not null,
    csl_i smallint not null
);

create table manager_reports (
    id serial primary key,
    tuple text not null,
    username_i smallint not null,
    msl_i smallint not null,
    asl_i smallint not null,
    csl_i smallint not null
);
