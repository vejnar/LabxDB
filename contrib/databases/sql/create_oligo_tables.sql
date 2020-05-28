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

CREATE OR REPLACE FUNCTION {schema}.insert_record(data json) RETURNS void AS $$
DECLARE
  oln integer;
  osep text;
  name text;
  x json;
BEGIN
  LOCK TABLE {schema}.item IN EXCLUSIVE MODE;
  SELECT INTO oln MAX(oligo_number) FROM {schema}.item;
  IF oln is NULL THEN
    oln := 0;
  END IF;
  FOR x IN SELECT * FROM json_array_elements(data)
  LOOP
    oln := oln + 1;
    name := x->>'name';
    IF SUBSTRING(name, 1, 1) = '_' OR SUBSTRING(name, 1, 1) = '-' OR SUBSTRING(name, 1, 1) = ' ' THEN
      osep := '';
    ELSE
      osep := '_';
    END IF;
    INSERT INTO {schema}.item (oligo_number,name,description,sequence,author,date_insert,date_order,status) VALUES (oln, CONCAT(CAST(oln AS text), osep, name), x->>'description', x->>'sequence', x->>'author', to_date(x->>'date_insert', 'YYYY-MM-DD'), to_date(x->>'date_order', 'YYYY-MM-DD'), x->>'status');
  END LOOP;
END;
$$ LANGUAGE plpgsql;

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
