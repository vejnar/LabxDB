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

CREATE OR REPLACE FUNCTION {schema}.insert_record(data json) RETURNS void AS $$
DECLARE
  yn integer;
  x json;
BEGIN
  LOCK TABLE {schema}.line IN EXCLUSIVE MODE;
  SELECT INTO yn MAX(y_number) FROM {schema}.line;
  IF yn is NULL THEN
    yn := 0;
  END IF;
  FOR x IN SELECT * FROM json_array_elements(data)
  LOOP
    yn := yn + 1;
    INSERT INTO {schema}.line (y_number,name,genotype,date_birth,father_id,father_name,mother_id,mother_name,number_fish,number_tank,author,genotyping,terminated,notes) VALUES (yn, x->>'name', x->>'genotype', to_date(x->>'date_birth', 'YYYY-MM-DD'), x->>'father_id', x->>'father_name', x->>'mother_id', x->>'mother_name', (x->>'number_fish')::int, (x->>'number_tank')::int, x->>'author', x->>'genotyping', (x->>'terminated')::boolean, x->>'notes');
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
GRANT SELECT,INSERT,UPDATE,DELETE ON TABLE {schema}.line TO lab;
GRANT SELECT,UPDATE ON TABLE {schema}.line_line_id_seq TO lab;
GRANT SELECT,INSERT,UPDATE,DELETE ON TABLE {schema}.option TO lab;
GRANT SELECT,UPDATE ON TABLE {schema}.option_option_id_seq TO lab;
