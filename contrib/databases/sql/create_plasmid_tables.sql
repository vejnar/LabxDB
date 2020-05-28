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

CREATE OR REPLACE FUNCTION {schema}.insert_record(data json) RETURNS void AS $$
DECLARE
  oln integer;
  osep text;
  map_filename text;
  x json;
BEGIN
  LOCK TABLE {schema}.item IN EXCLUSIVE MODE;
  SELECT INTO oln MAX(plasmid_number) FROM {schema}.item;
  IF oln is NULL THEN
    oln := 0;
  END IF;
  FOR x IN SELECT * FROM json_array_elements(data)
  LOOP
    oln := oln + 1;
    map_filename := x->>'map_filename';
    IF CHAR_LENGTH(map_filename) > 0 THEN
      IF SUBSTRING(map_filename, 1, 1) = '_' OR SUBSTRING(map_filename, 1, 1) = '-' OR SUBSTRING(map_filename, 1, 1) = ' ' THEN
        osep := '';
      ELSE
        osep := '_';
      END IF;
        map_filename := CONCAT(CAST(oln AS text), osep, map_filename);
    ELSE
      map_filename := NULL;
    END IF;
    INSERT INTO {schema}.item (plasmid_number,name,author,description,sequence,sequence_insert,map_img,map_filename,antibiotic,linearize_sense,promoter_sense,vector,cloning_strategy,glycerol_stock,missing,date_insert) VALUES (oln, x->>'name', x->>'author', x->>'description', x->>'sequence', x->>'sequence_insert', x->>'map_img', map_filename, x->>'antibiotic', x->>'linearize_sense', x->>'promoter_sense', x->>'vector', x->>'cloning_strategy', (x->>'glycerol_stock')::boolean, (x->>'missing')::boolean, to_date(x->>'date_insert', 'YYYY-MM-DD'));
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
