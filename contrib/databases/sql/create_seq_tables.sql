CREATE SCHEMA IF NOT EXISTS {schema};

CREATE TABLE {schema}.project (
    project_id serial not null,
    project_ref varchar(50),
    project_name varchar(100),
    label_short varchar(100),
    label_long varchar(255),
    scientist varchar(255),
    external_scientist varchar(255),
    sra_ref varchar(50),
    UNIQUE (project_ref),
    PRIMARY KEY (project_id));

CREATE TABLE {schema}.sample (
    sample_id serial not null,
    sample_ref varchar(50),
    project_ref varchar(50),
    label_short varchar(100),
    label_long varchar(255),
    species varchar(10),
    strain_maternal varchar(50),
    strain_paternal varchar(50),
    genotype varchar(50),
    ploidy varchar(50),
    age_hpf real,
    stage varchar(50),
    tissue varchar(50),
    condition varchar(50),
    treatment varchar(255),
    selection varchar(50),
    molecule varchar(50),
    library_protocol varchar(50),
    adapter_5p varchar(50),
    adapter_3p varchar(50),
    track_priority integer,
    track_color varchar(50),
    sra_ref varchar(255),
    notes varchar(255),
    UNIQUE (sample_ref),
    PRIMARY KEY (sample_id));

CREATE TABLE {schema}.replicate (
    replicate_id serial not null,
    replicate_ref varchar(50),
    replicate_order integer,
    sample_ref varchar(50),
    label_short varchar(100),
    label_long varchar(255),
    sra_ref varchar(255),
    publication_ref varchar(50),
    notes varchar(255),
    UNIQUE (replicate_ref),
    PRIMARY KEY (replicate_id));

CREATE TABLE {schema}.run (
    run_id serial not null,
    run_ref varchar(50),
    run_order integer,
    replicate_ref varchar(50),
    tube_label varchar(100),
    barcode varchar(50),
    second_barcode varchar(50),
    request_ref varchar(50),
    request_date date,
    failed boolean,
    flowcell varchar(50),
    platform varchar(50),
    quality_scores varchar(50),
    directional boolean,
    paired boolean,
    r1_strand varchar(1),
    spots bigint,
    max_read_length integer,
    sra_ref text,
    notes varchar(255),
    UNIQUE (run_ref),
    PRIMARY KEY (run_id));

CREATE TABLE {schema}.option (
    option_id serial not null,
    group_name varchar(50) not null,
    option varchar(50) not null,
    UNIQUE (group_name, option),
    PRIMARY KEY (option_id));

CREATE TABLE {schema}.publication (
    publication_id serial not null,
    publication_ref varchar(50),
    title varchar(255),
    publication_date date,
    pubmed_id varchar(50),
    sra_ref text,
    UNIQUE (publication_ref),
    PRIMARY KEY (publication_id));

CREATE OR REPLACE FUNCTION {schema}.get_next_id(prefix text, current_id text) RETURNS text AS $$
DECLARE
  n integer;
BEGIN
  IF current_id is NULL THEN
    n := 1;
  ELSE
    SELECT INTO n CAST(substring(current_id from LENGTH(prefix)+1) AS integer) + 1;
  END IF;
  IF n <= 999999 THEN
    RETURN CONCAT(prefix, LPAD(n::text, 6, '0'));
  ELSE
    RETURN CONCAT(prefix, n::text);
  END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION {schema}.create_new_ids(prefix text, new_run boolean, data json, OUT k text[], OUT ids text[], OUT serials bigint[]) AS $$
DECLARE
  i integer;
  e text;
  x text;
  t text;
BEGIN
  LOCK TABLE {schema}.replicate IN EXCLUSIVE MODE;
  LOCK TABLE {schema}.sample IN EXCLUSIVE MODE;
  LOCK TABLE {schema}.project IN EXCLUSIVE MODE;
  -- Update run order
  i := 0;
  FOR x IN SELECT * FROM json_array_elements((data->>'run')::json)
  LOOP
    -- Add new run
    raise notice 'Value: %', x;
    IF new_run IS TRUE THEN
      SELECT INTO t {schema}.get_next_id(CONCAT(prefix, 'R'), MAX(run_ref)) FROM {schema}.run WHERE run_ref LIKE CONCAT(prefix, '%');
      UPDATE {schema}.run SET run_ref=t, run_order=1 WHERE run_ref=trim('"' FROM x);
    ELSE
      t := trim('"' FROM x);
    END IF;
    -- Update run order & replicate ref (only for run append to a replicate)
    e := (data->>'run_append')::json -> i;
    raise notice 'Value e: %', e;
    IF e != 'null' THEN
      UPDATE {schema}.run SET replicate_ref=trim('"' FROM e), run_order=(SELECT COUNT(*)+1 FROM {schema}.run WHERE replicate_ref=trim('"' FROM e)) WHERE run_ref=t;
    END IF;
    -- Save
    k := array_append(k, 'run');
    ids := array_append(ids, t);
    serials := array_append(serials, NULL);
    i := i + 1;
  END LOOP;
  -- Replicate
  i := 0;
  FOR x IN SELECT * FROM json_array_elements((data->>'replicate')::json)
  LOOP
    -- Add new replicate
    raise notice 'Value: %', x;
    SELECT INTO t {schema}.get_next_id(CONCAT(prefix, 'N'), MAX(replicate_ref)) FROM {schema}.replicate WHERE replicate_ref LIKE CONCAT(prefix, '%');
    INSERT INTO {schema}.replicate (replicate_ref,replicate_order,label_short) VALUES (t, 1, trim('"' FROM x));
    -- Update new replicate order & sample ref (only for replicate append to a sample)
    e := (data->>'replicate_append')::json -> i;
    raise notice 'Value e: %', e;
    IF e != 'null' THEN
      UPDATE {schema}.replicate SET sample_ref=trim('"' FROM e), replicate_order=(SELECT COUNT(*)+1 FROM {schema}.replicate WHERE sample_ref=trim('"' FROM e)) WHERE replicate_ref=trim('"' FROM t);
    END IF;
    -- Save
    k := array_append(k, 'replicate');
    ids := array_append(ids, t);
    serials := array_append(serials, LASTVAL());
    i := i + 1;
  END LOOP;
  -- Sample
  i := 0;
  FOR x IN SELECT * FROM json_array_elements((data->>'sample')::json)
  LOOP
    -- Add new sample
    raise notice 'Value: %', x;
    SELECT INTO t {schema}.get_next_id(CONCAT(prefix, 'S'), MAX(sample_ref)) FROM {schema}.sample WHERE sample_ref LIKE CONCAT(prefix, '%');
    INSERT INTO {schema}.sample (sample_ref,label_short) VALUES (t, trim('"' FROM x));
    -- Update project ref (only for sample append to a project)
    e := (data->>'sample_append')::json -> i;
    raise notice 'Value e: %', e;
    IF e != 'null' THEN
      UPDATE {schema}.sample SET project_ref=trim('"' FROM e) WHERE sample_ref=trim('"' FROM t);
    END IF;
    -- Save
    k := array_append(k, 'sample');
    ids := array_append(ids, t);
    serials := array_append(serials, LASTVAL());
    i := i + 1;
  END LOOP;
  -- Project
  FOR x IN SELECT * FROM json_array_elements((data->>'project')::json)
  LOOP
    -- Add new project
    raise notice 'Value: %', x;
    SELECT INTO t {schema}.get_next_id(CONCAT(prefix, 'P'), MAX(project_ref)) FROM {schema}.project WHERE project_ref LIKE CONCAT(prefix, '%');
    INSERT INTO {schema}.project (project_ref,label_short) VALUES (t, trim('"' FROM x));
    -- Save
    k := array_append(k, 'project');
    ids := array_append(ids, t);
    serials := array_append(serials, LASTVAL());
  END LOOP;
END;
$$ LANGUAGE plpgsql;

GRANT USAGE ON SCHEMA {schema} TO lab;
GRANT SELECT,INSERT,UPDATE,DELETE ON {schema}.project to lab;
GRANT SELECT,INSERT,UPDATE,DELETE ON {schema}.sample to lab;
GRANT SELECT,INSERT,UPDATE,DELETE ON {schema}.replicate to lab;
GRANT SELECT,INSERT,UPDATE,DELETE ON {schema}.run to lab;
GRANT SELECT,INSERT,UPDATE,DELETE ON {schema}.option to lab;
GRANT SELECT,INSERT,UPDATE,DELETE ON {schema}.publication to lab;

GRANT SELECT,UPDATE ON TABLE {schema}.project_project_id_seq TO lab;
GRANT SELECT,UPDATE ON TABLE {schema}.sample_sample_id_seq TO lab;
GRANT SELECT,UPDATE ON TABLE {schema}.replicate_replicate_id_seq TO lab;
GRANT SELECT,UPDATE ON TABLE {schema}.run_run_id_seq TO lab;
GRANT SELECT,UPDATE ON TABLE {schema}.option_option_id_seq TO lab;
GRANT SELECT,UPDATE ON TABLE {schema}.publication_publication_id_seq TO lab;
