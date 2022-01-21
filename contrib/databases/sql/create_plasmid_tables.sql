CREATE SCHEMA {schema};

CREATE TABLE {schema}.item (
    item_id serial not null,
    plasmid_number integer not null,
    number_suffix varchar(5),
    name varchar(255),
    author varchar(50),
    description text,
    sequence text,
    sequence_insert text,
    map_img text,
    map_filename varchar(255) CONSTRAINT check_alnum CHECK (map_filename ~* '^[A-Z0-9._-]+$') UNIQUE,
    antibiotic varchar(50),
    linearize_sense varchar(50),
    promoter_sense varchar(50),
    vector varchar(100),
    cloning_strategy text,
    glycerol_stock boolean,
    missing boolean,
    date_insert date default CURRENT_DATE,
    PRIMARY KEY (item_id));

CREATE UNIQUE INDEX unique_number_suffix ON {schema}.item (plasmid_number,number_suffix) WHERE number_suffix IS NOT NULL;
CREATE UNIQUE INDEX unique_number ON {schema}.item (plasmid_number) WHERE number_suffix IS NULL;
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
