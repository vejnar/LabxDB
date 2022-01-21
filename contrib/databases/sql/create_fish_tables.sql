CREATE SCHEMA {schema};

CREATE TABLE {schema}.line (
    line_id serial not null,
    y_number integer not null,
    name varchar(255),
    genotype varchar(50),
    date_birth date,
    father_id varchar(50),
    father_name varchar(255),
    mother_id varchar(50),
    mother_name varchar(255),
    number_fish integer,
    number_tank integer,
    author varchar(50),
    genotyping text,
    terminated bool,
    notes text,
    zfin_ref varchar(50),
    PRIMARY KEY (line_id));

CREATE UNIQUE INDEX unique_y_number ON {schema}.line (y_number);

CREATE TABLE {schema}.option (
    option_id serial not null,
    group_name varchar(50) not null,
    option varchar(50) not null,
    UNIQUE (group_name, option),
    PRIMARY KEY (option_id));

GRANT USAGE ON SCHEMA {schema} TO lab;
GRANT SELECT,INSERT,UPDATE,DELETE ON TABLE {schema}.line TO lab;
GRANT SELECT,UPDATE ON TABLE {schema}.line_line_id_seq TO lab;
GRANT SELECT,INSERT,UPDATE,DELETE ON TABLE {schema}.option TO lab;
GRANT SELECT,UPDATE ON TABLE {schema}.option_option_id_seq TO lab;
