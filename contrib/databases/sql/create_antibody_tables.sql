CREATE SCHEMA {schema};

CREATE TABLE {schema}.item (
    item_id serial not null,
    antibody_id varchar(50) CONSTRAINT check_alnum CHECK (antibody_id ~* '^[A-Z0-9]+$') UNIQUE,
    name varchar(255),
    storage_temp integer,
    host_animal varchar(50),
    size_confirmed varchar(50),
    wb_confirmed varchar(255),
    icc_if_confirmed varchar(255),
    ip_confirmed varchar(255),
    app_confirmed text,
    practical_notes text,
    clonal varchar(20),
    mol_weight varchar(50),
    app_suggested text,
    size_suggested varchar(50),
    manufacturer varchar(255),
    manufacturer_ref varchar(255),
    concentration varchar(50),
    custom_antibody boolean default FALSE,
    date_received date default CURRENT_DATE,
    lot_num varchar(255),
    PRIMARY KEY (item_id));

CREATE UNIQUE INDEX unique_antibody_id ON {schema}.item (antibody_id);

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
