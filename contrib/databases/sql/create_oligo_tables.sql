CREATE SCHEMA {schema};

CREATE TABLE {schema}.item (
    item_id serial not null,
    oligo_number integer not null,
    number_suffix varchar(5),
    name varchar(255),
    description text,
    sequence text,
    author varchar(50),
    date_insert date default CURRENT_DATE,
    date_order date,
    status varchar(50),
    PRIMARY KEY (item_id));

CREATE UNIQUE INDEX unique_number_suffix ON {schema}.item (oligo_number,number_suffix) WHERE number_suffix IS NOT NULL;
CREATE UNIQUE INDEX unique_number ON {schema}.item (oligo_number) WHERE number_suffix IS NULL;
CREATE UNIQUE INDEX unique_name ON {schema}.item (name);

CREATE TABLE {schema}.option (
    option_id serial not null,
    group_name varchar(50) not null,
    option varchar(50) not null,
    UNIQUE (group_name, option),
    PRIMARY KEY (option_id));

GRANT USAGE ON SCHEMA {schema} TO lab;
GRANT SELECT,INSERT,UPDATE,DELETE ON TABLE {schema}.item TO lab;
GRANT SELECT,UPDATE ON TABLE {schema}.item_item_id_seq TO lab;
GRANT SELECT,INSERT,UPDATE,DELETE ON TABLE {schema}.option TO lab;
GRANT SELECT,UPDATE ON TABLE {schema}.option_option_id_seq TO lab;
