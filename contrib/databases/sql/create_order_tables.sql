CREATE SCHEMA {schema};

CREATE TABLE {schema}.item (
    item_id serial not null,
    item varchar(255),
    item_ref varchar(255),
    item_size varchar(255),
    provider varchar(255),
    provider_stockroom boolean,
    quantity integer,
    unit_price numeric(8,2),
    total_price numeric(8,2),
    status varchar(50),
    recipient varchar(50),
    date_insert date default CURRENT_DATE,
    date_order date,
    manufacturer varchar(255),
    manufacturer_ref varchar(255),
    funding varchar(255),
    PRIMARY KEY (item_id));

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
